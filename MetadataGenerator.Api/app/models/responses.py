"""Response models for API endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ImageMetadataResponse(BaseModel):
    """Response payload for image metadata extraction."""

    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the uploaded file")
    description: str = Field(..., description="AI-generated description (German)")
    keywords: list[str] = Field(..., description="AI-generated keywords (German)")
    caption: str = Field(..., description="AI-generated caption (German)")
    exif: dict[str, str | float | None] = Field(
        default_factory=dict,
        description="EXIF metadata extracted from the image",
    )
    processing_time_ms: int = Field(..., ge=0, description="Processing time in milliseconds")


class AudioMetadataResponse(BaseModel):
    """Response payload for audio metadata extraction."""

    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the uploaded file")
    description: str = Field(..., description="AI-generated description (German)")
    keywords: list[str] = Field(..., description="AI-generated keywords (German)")
    summary: str = Field(..., description="AI-generated summary (German)")
    duration_seconds: float | None = Field(default=None, description="Audio duration in seconds")
    processing_time_ms: int = Field(..., ge=0, description="Processing time in milliseconds")


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str = Field(..., description="Human-readable error message")
    error_code: str = Field(default="UNKNOWN", description="Machine-readable error code")


# ---------------------------------------------------------------------------
# Batch response models
# ---------------------------------------------------------------------------


class FileAnalysisResult(BaseModel):
    """Result for a single file within a batch analysis."""

    file_name: str = Field(..., description="Original file name")
    file_index: int = Field(..., ge=0, description="Upload order index")
    status: Literal["success", "error"] = Field(..., description="Processing outcome")
    file_type: Literal["image", "audio", "unknown"] = Field(
        ..., description="Detected file category"
    )
    metadata: ImageMetadataResponse | AudioMetadataResponse | None = Field(
        default=None,
        description="Metadata payload (present when status='success')",
    )
    error: ErrorResponse | None = Field(
        default=None,
        description="Error details (present when status='error')",
    )


class BatchAnalysisResponse(BaseModel):
    """Aggregated response for a batch file analysis request."""

    results: list[FileAnalysisResult] = Field(..., description="Per-file results in upload order")
    total_files: int = Field(..., ge=0, description="Total files submitted")
    successful: int = Field(..., ge=0, description="Number of successfully analysed files")
    failed: int = Field(..., ge=0, description="Number of failed files")
    total_processing_time_ms: int = Field(
        ..., ge=0, description="Total wall-clock processing time in milliseconds"
    )
