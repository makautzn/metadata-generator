"""Pydantic models for Azure Content Understanding analysis results."""

from pydantic import BaseModel, Field


class ImageAnalysisResult(BaseModel):
    """Structured metadata extracted from an image via Azure Content Understanding."""

    description: str = Field(
        ...,
        min_length=1,
        description="A descriptive text summarising the image content (German)",
    )
    keywords: list[str] = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Relevant keywords extracted from the image (German)",
    )
    caption: str = Field(
        ...,
        min_length=1,
        description="A concise caption for the image (German)",
    )


class AudioAnalysisResult(BaseModel):
    """Structured metadata extracted from an audio file via Azure Content Understanding."""

    description: str = Field(
        ...,
        min_length=1,
        description="A descriptive text summarising the audio content (German)",
    )
    keywords: list[str] = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Relevant keywords extracted from the audio (German)",
    )
    summary: str = Field(
        ...,
        min_length=1,
        description="A concise summary of the audio content (German)",
    )


class AnalysisError(BaseModel):
    """Structured error information from the analysis service."""

    error_code: str = Field(
        ...,
        description="Machine-readable error code (e.g. AZURE_HTTP_429)",
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
    )
