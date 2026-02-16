"""Audio file utilities for duration extraction and validation."""

from __future__ import annotations

import io
import logging
from typing import Any

import mutagen

from app.utils.file_validation import MAX_AUDIO_DURATION_SECONDS, SUPPORTED_AUDIO_TYPES

logger = logging.getLogger(__name__)

_mutagen_file = mutagen.File  # type: ignore[attr-defined]


def get_audio_duration(file_bytes: bytes, file_name: str) -> float | None:
    """Return the duration of an audio file in seconds, or ``None`` on failure."""
    try:
        audio: Any = _mutagen_file(io.BytesIO(file_bytes), filename=file_name)
        if audio is not None and audio.info is not None:
            return float(audio.info.length)
    except Exception:
        logger.debug("Could not determine audio duration for %s", file_name)
    return None


def validate_audio_upload(
    content_type: str | None,
    file_bytes: bytes,
    file_name: str,
) -> tuple[str, float | None]:
    """Validate an audio upload and return ``(mime_type, duration_seconds)``.

    Raises ``ValueError`` with a descriptive message on failure.
    """
    # --- Content-type check -----------------------------------------------
    mime = content_type or "application/octet-stream"
    if mime not in SUPPORTED_AUDIO_TYPES:
        supported = ", ".join(sorted(SUPPORTED_AUDIO_TYPES))
        msg = f"Nicht unterstützter Audio-Dateityp: {mime}. Unterstützte Formate: {supported}"
        raise ValueError(msg)

    # --- Duration check ---------------------------------------------------
    duration = get_audio_duration(file_bytes, file_name)
    if duration is not None and duration > MAX_AUDIO_DURATION_SECONDS:
        max_min = int(MAX_AUDIO_DURATION_SECONDS // 60)
        msg = f"Audiodatei ist zu lang ({duration:.0f}s). Maximum: {max_min} Minuten."
        raise ValueError(msg)

    return mime, duration
