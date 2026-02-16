"""Image metadata extraction API endpoint.

Handles single-image uploads: validates, extracts EXIF, calls the Azure
Content Understanding service, and returns combined metadata.
"""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.core.dependencies import get_content_understanding_service
from app.core.exceptions import ContentUnderstandingError
from app.models.responses import ErrorResponse, ImageMetadataResponse
from app.services.content_understanding import ContentUnderstandingServiceProtocol
from app.utils.exif_extraction import extract_exif
from app.utils.file_validation import (
    validate_image_content_type,
    validate_image_size,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Image Analysis"])


@router.post(
    "/analyze/image",
    response_model=ImageMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse a single image and extract metadata",
    responses={
        413: {"model": ErrorResponse, "description": "File too large"},
        422: {"model": ErrorResponse, "description": "Unsupported file type"},
        500: {"model": ErrorResponse, "description": "Analysis service error"},
    },
)
async def analyze_image(
    file: UploadFile,
    cu_service: ContentUnderstandingServiceProtocol = Depends(get_content_understanding_service),
) -> ImageMetadataResponse:
    """Upload an image and receive AI-generated metadata plus EXIF data."""
    start = time.monotonic()

    # --- Read file bytes --------------------------------------------------
    file_bytes = await file.read()
    file_size = len(file_bytes)
    file_name = file.filename or "unknown"

    # --- Validate size ----------------------------------------------------
    try:
        validate_image_size(file_size)
    except ValueError as exc:
        logger.warning("Image too large: %s (%d bytes)", file_name, file_size)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(exc),
        ) from exc

    # --- Validate content type --------------------------------------------
    header_bytes = file_bytes[:16]
    try:
        detected_mime = validate_image_content_type(file.content_type, header_bytes)
    except ValueError as exc:
        logger.warning("Invalid image type for %s: %s", file_name, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    # --- Extract EXIF -----------------------------------------------------
    exif_data = extract_exif(file_bytes)

    # --- AI analysis ------------------------------------------------------
    try:
        ai_result = await cu_service.analyze_image(file_bytes, detected_mime)
    except ContentUnderstandingError as exc:
        logger.error("AI analysis failed for %s: %s", file_name, exc.message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analyse fehlgeschlagen: {exc.message}",
        ) from exc

    elapsed_ms = int((time.monotonic() - start) * 1000)

    return ImageMetadataResponse(
        file_name=file_name,
        file_size=file_size,
        mime_type=detected_mime,
        description=ai_result.description,
        keywords=ai_result.keywords,
        caption=ai_result.caption,
        exif=exif_data,
        processing_time_ms=elapsed_ms,
    )
