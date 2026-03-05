"""Audio metadata extraction API endpoint.

Provides two modes of operation:
1. **Synchronous** – ``POST /analyze/audio`` blocks until analysis
   completes (only practical for short files / direct API use).
2. **Async submit + poll** – ``POST /analyze/audio/submit`` returns a
   job ID immediately; ``GET /analyze/audio/status/{job_id}`` is polled
   by the frontend until the result is ready.  This avoids proxy
   timeouts for long-running audio analysis.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.core.dependencies import get_content_understanding_service
from app.core.exceptions import ContentUnderstandingError
from app.models.responses import (
    AudioJobStatusResponse,
    AudioJobSubmitResponse,
    AudioMetadataResponse,
    ErrorResponse,
)
from app.services.content_understanding import ContentUnderstandingServiceProtocol
from app.utils.audio_utils import validate_audio_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Audio Analysis"])

# ---------------------------------------------------------------------------
# In-memory job store (sufficient for single-process PoC)
# ---------------------------------------------------------------------------


@dataclass
class _AudioJob:
    job_id: str
    status: Literal["processing", "completed", "failed"] = "processing"
    result: AudioMetadataResponse | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.monotonic)


_jobs: dict[str, _AudioJob] = {}

# Auto-expire completed/failed jobs after 30 minutes
_JOB_TTL_SECONDS = 1800


def _cleanup_expired_jobs() -> None:
    now = time.monotonic()
    expired = [jid for jid, j in _jobs.items() if now - j.created_at > _JOB_TTL_SECONDS]
    for jid in expired:
        del _jobs[jid]


# ---------------------------------------------------------------------------
# Synchronous endpoint (kept for backwards compatibility / direct API use)
# ---------------------------------------------------------------------------


@router.post(
    "/analyze/audio",
    response_model=AudioMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse a single audio file and extract metadata",
    responses={
        422: {"model": ErrorResponse, "description": "Invalid file type or duration"},
        500: {"model": ErrorResponse, "description": "Analysis service error"},
    },
)
async def analyze_audio(
    file: UploadFile,
    cu_service: ContentUnderstandingServiceProtocol = Depends(get_content_understanding_service),
) -> AudioMetadataResponse:
    """Upload an audio file and receive AI-generated metadata."""
    start = time.monotonic()

    # --- Read file bytes --------------------------------------------------
    file_bytes = await file.read()
    file_size = len(file_bytes)
    file_name = file.filename or "unknown"

    # --- Validate format and duration -------------------------------------
    try:
        mime_type, duration = validate_audio_upload(
            content_type=file.content_type,
            file_bytes=file_bytes,
            file_name=file_name,
        )
    except ValueError as exc:
        logger.warning("Audio validation failed for %s: %s", file_name, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    # --- AI analysis ------------------------------------------------------
    try:
        ai_result = await cu_service.analyze_audio(file_bytes, mime_type)
    except ContentUnderstandingError as exc:
        logger.error("AI analysis failed for %s: %s", file_name, exc.message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analyse fehlgeschlagen: {exc.message}",
        ) from exc

    elapsed_ms = int((time.monotonic() - start) * 1000)

    return AudioMetadataResponse(
        file_name=file_name,
        file_size=file_size,
        mime_type=mime_type,
        description=ai_result.description,
        keywords=ai_result.keywords,
        summary=ai_result.summary,
        duration_seconds=duration,
        processing_time_ms=elapsed_ms,
    )


# ---------------------------------------------------------------------------
# Async submit + poll endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/analyze/audio/submit",
    response_model=AudioJobSubmitResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit an audio file for async analysis",
    responses={
        422: {"model": ErrorResponse, "description": "Invalid file type or duration"},
    },
)
async def submit_audio(
    file: UploadFile,
    cu_service: ContentUnderstandingServiceProtocol = Depends(get_content_understanding_service),
) -> AudioJobSubmitResponse:
    """Accept an audio file, start background analysis, return job ID."""
    _cleanup_expired_jobs()

    file_bytes = await file.read()
    file_size = len(file_bytes)
    file_name = file.filename or "unknown"

    try:
        mime_type, duration = validate_audio_upload(
            content_type=file.content_type,
            file_bytes=file_bytes,
            file_name=file_name,
        )
    except ValueError as exc:
        logger.warning("Audio validation failed for %s: %s", file_name, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    job_id = uuid.uuid4().hex
    job = _AudioJob(job_id=job_id)
    _jobs[job_id] = job

    # Fire-and-forget background task
    asyncio.create_task(
        _run_audio_analysis(job, cu_service, file_bytes, file_size, file_name, mime_type, duration)
    )

    logger.info("Audio job %s submitted for %s", job_id, file_name)
    return AudioJobSubmitResponse(job_id=job_id)


@router.get(
    "/analyze/audio/status/{job_id}",
    response_model=AudioJobStatusResponse,
    summary="Poll audio analysis job status",
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
    },
)
async def get_audio_status(job_id: str) -> AudioJobStatusResponse:
    """Return the current status of an audio analysis job."""
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found or expired",
        )
    return AudioJobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        result=job.result,
        error=job.error,
    )


async def _run_audio_analysis(
    job: _AudioJob,
    cu_service: ContentUnderstandingServiceProtocol,
    file_bytes: bytes,
    file_size: int,
    file_name: str,
    mime_type: str,
    duration: float | None,
) -> None:
    """Background coroutine that runs the Azure CU analysis."""
    start = time.monotonic()
    dur_str = f" ({duration:.0f}s audio)" if duration else ""
    logger.info("Audio job %s starting analysis for %s%s", job.job_id, file_name, dur_str)
    try:
        ai_result = await cu_service.analyze_audio(file_bytes, mime_type)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        job.result = AudioMetadataResponse(
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            description=ai_result.description,
            keywords=ai_result.keywords,
            summary=ai_result.summary,
            duration_seconds=duration,
            processing_time_ms=elapsed_ms,
        )
        job.status = "completed"
        logger.info("Audio job %s completed in %dms", job.job_id, elapsed_ms)
    except ContentUnderstandingError as exc:
        job.status = "failed"
        job.error = f"Analyse fehlgeschlagen: {exc.message}"
        logger.error("Audio job %s failed: %s", job.job_id, exc.message)
    except Exception as exc:
        job.status = "failed"
        job.error = f"Unerwarteter Fehler: {exc}"
        logger.exception("Audio job %s unexpected error", job.job_id)
