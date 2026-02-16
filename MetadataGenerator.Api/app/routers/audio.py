"""Audio metadata extraction API endpoint.

Handles single-audio uploads: validates format and duration, calls the
Azure Content Understanding service, and returns structured metadata.
"""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.core.dependencies import get_content_understanding_service
from app.core.exceptions import ContentUnderstandingError
from app.models.responses import AudioMetadataResponse, ErrorResponse
from app.services.content_understanding import ContentUnderstandingServiceProtocol
from app.utils.audio_utils import validate_audio_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Audio Analysis"])


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
