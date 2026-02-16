"""Batch file analysis API endpoint.

Accepts up to 20 files (images and/or audio), analyses them concurrently
via the Azure Content Understanding service, and returns aggregated results
preserving upload order.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.core.dependencies import get_content_understanding_service
from app.core.exceptions import ContentUnderstandingError
from app.models.responses import (
    AudioMetadataResponse,
    BatchAnalysisResponse,
    ErrorResponse,
    FileAnalysisResult,
    ImageMetadataResponse,
)
from app.services.content_understanding import ContentUnderstandingServiceProtocol
from app.utils.audio_utils import validate_audio_upload
from app.utils.exif_extraction import extract_exif
from app.utils.file_validation import (
    SUPPORTED_AUDIO_TYPES,
    SUPPORTED_IMAGE_TYPES,
    validate_image_content_type,
    validate_image_size,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Batch Analysis"])

MAX_BATCH_FILES = 20
_CONCURRENCY_LIMIT = 5


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _classify_file(content_type: str | None) -> str:
    """Return ``'image'``, ``'audio'``, or ``'unknown'`` for a MIME type."""
    mime = content_type or "application/octet-stream"
    if mime in SUPPORTED_IMAGE_TYPES:
        return "image"
    if mime in SUPPORTED_AUDIO_TYPES:
        return "audio"
    return "unknown"


async def _process_image(
    file_bytes: bytes,
    file_name: str,
    content_type: str | None,
    cu_service: ContentUnderstandingServiceProtocol,
) -> ImageMetadataResponse:
    """Validate and analyse a single image file."""
    start = time.monotonic()
    header = file_bytes[:32]
    mime_type = validate_image_content_type(content_type, header)
    validate_image_size(len(file_bytes))
    exif_data = extract_exif(file_bytes)
    ai_result = await cu_service.analyze_image(file_bytes, mime_type)
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return ImageMetadataResponse(
        file_name=file_name,
        file_size=len(file_bytes),
        mime_type=mime_type,
        description=ai_result.description,
        keywords=ai_result.keywords,
        caption=ai_result.caption,
        exif=exif_data,
        processing_time_ms=elapsed_ms,
    )


async def _process_audio(
    file_bytes: bytes,
    file_name: str,
    content_type: str | None,
    cu_service: ContentUnderstandingServiceProtocol,
) -> AudioMetadataResponse:
    """Validate and analyse a single audio file."""
    start = time.monotonic()
    mime_type, duration = validate_audio_upload(content_type, file_bytes, file_name)
    ai_result = await cu_service.analyze_audio(file_bytes, mime_type)
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return AudioMetadataResponse(
        file_name=file_name,
        file_size=len(file_bytes),
        mime_type=mime_type,
        description=ai_result.description,
        keywords=ai_result.keywords,
        summary=ai_result.summary,
        duration_seconds=duration,
        processing_time_ms=elapsed_ms,
    )


async def _process_one(
    index: int,
    file: UploadFile,
    cu_service: ContentUnderstandingServiceProtocol,
    semaphore: asyncio.Semaphore,
) -> FileAnalysisResult:
    """Process a single file within the batch, returning a result entry."""
    file_name = file.filename or f"file_{index}"
    file_type = _classify_file(file.content_type)

    async with semaphore:
        try:
            file_bytes = await file.read()

            if file_type == "image":
                metadata: Any = await _process_image(
                    file_bytes, file_name, file.content_type, cu_service
                )
            elif file_type == "audio":
                metadata = await _process_audio(
                    file_bytes, file_name, file.content_type, cu_service
                )
            else:
                return FileAnalysisResult(
                    file_name=file_name,
                    file_index=index,
                    status="error",
                    file_type="unknown",
                    error=ErrorResponse(
                        detail=f"Nicht unterstützter Dateityp: {file.content_type}",
                        error_code="UNSUPPORTED_TYPE",
                    ),
                )

            return FileAnalysisResult(
                file_name=file_name,
                file_index=index,
                status="success",
                file_type=file_type,
                metadata=metadata,
            )

        except ValueError as exc:
            return FileAnalysisResult(
                file_name=file_name,
                file_index=index,
                status="error",
                file_type=file_type,
                error=ErrorResponse(
                    detail=str(exc),
                    error_code="VALIDATION_ERROR",
                ),
            )

        except ContentUnderstandingError as exc:
            return FileAnalysisResult(
                file_name=file_name,
                file_index=index,
                status="error",
                file_type=file_type,
                error=ErrorResponse(
                    detail=exc.message,
                    error_code=exc.error_code,
                ),
            )

        except Exception as exc:
            logger.exception("Unexpected error processing %s", file_name)
            return FileAnalysisResult(
                file_name=file_name,
                file_index=index,
                status="error",
                file_type=file_type,
                error=ErrorResponse(
                    detail=str(exc),
                    error_code="INTERNAL_ERROR",
                ),
            )


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/analyze/batch",
    response_model=BatchAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse a batch of image and/or audio files",
    responses={
        422: {"model": ErrorResponse, "description": "Invalid request (too many files)"},
    },
)
async def analyze_batch(
    files: list[UploadFile],
    cu_service: ContentUnderstandingServiceProtocol = Depends(get_content_understanding_service),
) -> BatchAnalysisResponse:
    """Upload up to 20 files and receive AI-generated metadata for each."""
    start = time.monotonic()

    if not files:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Keine Dateien hochgeladen.",
        )

    if len(files) > MAX_BATCH_FILES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Maximal {MAX_BATCH_FILES} Dateien pro Anfrage erlaubt.",
        )

    semaphore = asyncio.Semaphore(_CONCURRENCY_LIMIT)
    tasks = [_process_one(i, f, cu_service, semaphore) for i, f in enumerate(files)]
    results = await asyncio.gather(*tasks)

    # Sort by file_index to guarantee order
    sorted_results = sorted(results, key=lambda r: r.file_index)
    successful = sum(1 for r in sorted_results if r.status == "success")
    failed = len(sorted_results) - successful
    elapsed_ms = int((time.monotonic() - start) * 1000)

    return BatchAnalysisResponse(
        results=sorted_results,
        total_files=len(sorted_results),
        successful=successful,
        failed=failed,
        total_processing_time_ms=elapsed_ms,
    )
