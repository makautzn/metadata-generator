"""Production webhook endpoint for external metadata extraction requests.

Accepts file references (URLs), authenticates via API key, processes files
asynchronously in the background, and delivers results to a callback URL.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
import uuid
from typing import Any, Literal

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

from app.core.dependencies import get_content_understanding_service, get_settings
from app.core.exceptions import ContentUnderstandingError
from app.models.responses import (
    AudioMetadataResponse,
    ErrorResponse,
    ImageMetadataResponse,
)
from app.services.content_understanding import ContentUnderstandingServiceProtocol
from app.utils.audio_utils import validate_audio_upload
from app.utils.file_validation import (
    validate_image_content_type,
    validate_image_size,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Webhook"])

# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class FileReference(BaseModel):
    """Reference to a file accessible via URL."""

    url: str = Field(..., description="Publicly accessible URL to the file")
    file_type: Literal["image", "audio"] = Field(..., description="Explicit file type declaration")
    reference_id: str | None = Field(
        default=None, description="Optional caller-defined correlation ID"
    )


class WebhookRequest(BaseModel):
    """Incoming webhook request body."""

    files: list[FileReference] = Field(..., min_length=1, description="File references to process")
    callback_url: HttpUrl = Field(..., description="URL to POST results to upon completion")


class WebhookAcceptedResponse(BaseModel):
    """Returned immediately on successful webhook submission."""

    job_id: str = Field(..., description="Unique job identifier")
    message: str = Field(default="Accepted", description="Status message")
    total_files: int = Field(..., description="Number of files queued")


class WebhookFileResult(BaseModel):
    """Result for a single file within a webhook callback payload."""

    reference_id: str | None = None
    file_url: str
    file_type: Literal["image", "audio"]
    status: Literal["success", "error"]
    metadata: ImageMetadataResponse | AudioMetadataResponse | None = None
    error: ErrorResponse | None = None


class WebhookCallbackPayload(BaseModel):
    """Payload delivered to the callback URL after processing."""

    job_id: str
    status: Literal["completed", "partial", "failed"]
    results: list[WebhookFileResult]
    total_files: int
    successful: int
    failed: int
    processing_time_ms: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DOWNLOAD_TIMEOUT = 60  # seconds per file download
_MAX_DOWNLOAD_SIZE = 200 * 1024 * 1024  # 200 MB safety cap


def _api_key_hash(key: str) -> str:
    """Return a truncated SHA-256 hash for safe logging."""
    return hashlib.sha256(key.encode()).hexdigest()[:12]


async def _download_file(url: str) -> tuple[bytes, str]:
    """Download a file from *url* and return ``(content, content_type)``."""
    async with httpx.AsyncClient(timeout=_DOWNLOAD_TIMEOUT) as client:
        resp = await client.get(url, follow_redirects=True)
        resp.raise_for_status()
        ct = resp.headers.get("content-type", "application/octet-stream").split(";")[0].strip()
        body = resp.content
        if len(body) > _MAX_DOWNLOAD_SIZE:
            msg = f"Downloaded file exceeds size limit ({len(body):,} bytes)"
            raise ValueError(msg)
        return body, ct


async def _process_webhook_file(
    ref: FileReference,
    cu_service: ContentUnderstandingServiceProtocol,
) -> WebhookFileResult:
    """Download and analyse one file reference."""
    try:
        file_bytes, content_type = await _download_file(ref.url)
    except Exception as exc:
        return WebhookFileResult(
            reference_id=ref.reference_id,
            file_url=ref.url,
            file_type=ref.file_type,
            status="error",
            error=ErrorResponse(
                detail=f"Download fehlgeschlagen: {exc}",
                error_code="DOWNLOAD_ERROR",
            ),
        )

    try:
        if ref.file_type == "image":
            return await _process_webhook_image(ref, file_bytes, content_type, cu_service)
        return await _process_webhook_audio(ref, file_bytes, content_type, cu_service)
    except ValueError as exc:
        return WebhookFileResult(
            reference_id=ref.reference_id,
            file_url=ref.url,
            file_type=ref.file_type,
            status="error",
            error=ErrorResponse(detail=str(exc), error_code="VALIDATION_ERROR"),
        )
    except ContentUnderstandingError as exc:
        return WebhookFileResult(
            reference_id=ref.reference_id,
            file_url=ref.url,
            file_type=ref.file_type,
            status="error",
            error=ErrorResponse(detail=exc.message, error_code=exc.error_code),
        )


async def _process_webhook_image(
    ref: FileReference,
    file_bytes: bytes,
    content_type: str,
    cu_service: ContentUnderstandingServiceProtocol,
) -> WebhookFileResult:
    start = time.monotonic()
    header = file_bytes[:32]
    mime = validate_image_content_type(content_type, header)
    validate_image_size(len(file_bytes))
    ai = await cu_service.analyze_image(file_bytes, mime)
    elapsed = int((time.monotonic() - start) * 1000)
    meta = ImageMetadataResponse(
        file_name=ref.url.rsplit("/", 1)[-1] or "image",
        file_size=len(file_bytes),
        mime_type=mime,
        description=ai.description,
        keywords=ai.keywords,
        caption=ai.caption,
        exif={},
        processing_time_ms=elapsed,
    )
    return WebhookFileResult(
        reference_id=ref.reference_id,
        file_url=ref.url,
        file_type="image",
        status="success",
        metadata=meta,
    )


async def _process_webhook_audio(
    ref: FileReference,
    file_bytes: bytes,
    content_type: str,
    cu_service: ContentUnderstandingServiceProtocol,
) -> WebhookFileResult:
    start = time.monotonic()
    file_name = ref.url.rsplit("/", 1)[-1] or "audio"
    mime, duration = validate_audio_upload(content_type, file_bytes, file_name)
    ai = await cu_service.analyze_audio(file_bytes, mime)
    elapsed = int((time.monotonic() - start) * 1000)
    meta = AudioMetadataResponse(
        file_name=file_name,
        file_size=len(file_bytes),
        mime_type=mime,
        description=ai.description,
        keywords=ai.keywords,
        summary=ai.summary,
        duration_seconds=duration,
        processing_time_ms=elapsed,
    )
    return WebhookFileResult(
        reference_id=ref.reference_id,
        file_url=ref.url,
        file_type="audio",
        status="success",
        metadata=meta,
    )


async def _run_webhook_job(
    job_id: str,
    request: WebhookRequest,
    cu_service: ContentUnderstandingServiceProtocol,
) -> None:
    """Background task: process all files and POST results to callback URL."""
    start = time.monotonic()

    tasks = [_process_webhook_file(ref, cu_service) for ref in request.files]
    results: list[WebhookFileResult] = list(await asyncio.gather(*tasks))

    successful = sum(1 for r in results if r.status == "success")
    failed = len(results) - successful
    elapsed = int((time.monotonic() - start) * 1000)

    overall: Any = "completed"
    if failed == len(results):
        overall = "failed"
    elif failed > 0:
        overall = "partial"

    payload = WebhookCallbackPayload(
        job_id=job_id,
        status=overall,
        results=results,
        total_files=len(results),
        successful=successful,
        failed=failed,
        processing_time_ms=elapsed,
    )

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                str(request.callback_url),
                json=payload.model_dump(mode="json"),
            )
            resp.raise_for_status()
            logger.info("Callback delivered for job %s (status %s)", job_id, resp.status_code)
    except Exception:
        logger.exception(
            "Failed to deliver callback for job %s to %s",
            job_id,
            request.callback_url,
        )


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/webhook/analyze",
    response_model=WebhookAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit files for async metadata extraction with callback delivery",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication failed"},
        422: {"model": ErrorResponse, "description": "Invalid request body"},
    },
)
async def webhook_analyze(
    body: WebhookRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str | None = Header(default=None),
    cu_service: ContentUnderstandingServiceProtocol = Depends(get_content_understanding_service),
    settings: Any = Depends(get_settings),
) -> WebhookAcceptedResponse:
    """Accept file references for background processing and callback delivery."""
    # --- Authentication ---------------------------------------------------
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API-Schlüssel fehlt. Bitte X-API-Key Header angeben.",
        )

    if x_api_key not in settings.webhook_api_keys:
        logger.warning("Invalid API key attempt: %s", _api_key_hash(x_api_key))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger API-Schlüssel.",
        )

    # --- Schedule background work -----------------------------------------
    job_id = str(uuid.uuid4())
    background_tasks.add_task(_run_webhook_job, job_id, body, cu_service)

    return WebhookAcceptedResponse(
        job_id=job_id,
        message="Accepted",
        total_files=len(body.files),
    )
