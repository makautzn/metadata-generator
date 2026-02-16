"""File validation utilities.

Provides MIME type validation via magic bytes and file size checks for
uploaded image and audio files.
"""

from __future__ import annotations

# Magic byte signatures for supported image formats
_IMAGE_SIGNATURES: dict[bytes, str] = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"II\x2a\x00": "image/tiff",  # Little-endian TIFF
    b"MM\x00\x2a": "image/tiff",  # Big-endian TIFF
    b"RIFF": "image/webp",  # WebP (starts with RIFF...WEBP)
}

SUPPORTED_IMAGE_TYPES: frozenset[str] = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/tiff",
        "image/webp",
    }
)

SUPPORTED_AUDIO_TYPES: frozenset[str] = frozenset(
    {
        "audio/mpeg",
        "audio/wav",
        "audio/x-wav",
        "audio/flac",
        "audio/ogg",
        "audio/mp4",
        "audio/x-m4a",
    }
)

MAX_IMAGE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
MAX_AUDIO_DURATION_SECONDS: float = 15 * 60.0  # 15 minutes


def detect_image_mime(header_bytes: bytes) -> str | None:
    """Detect image MIME type from the first bytes of a file.

    Returns the detected MIME type string or ``None`` if unrecognised.
    """
    for signature, mime in _IMAGE_SIGNATURES.items():
        if header_bytes.startswith(signature):
            # WebP needs an extra check: RIFF....WEBP
            if mime == "image/webp":
                if len(header_bytes) >= 12 and header_bytes[8:12] == b"WEBP":
                    return mime
                continue
            return mime
    return None


def validate_image_content_type(declared: str | None, header_bytes: bytes) -> str:
    """Validate and return the canonical MIME type for an image upload.

    Raises ``ValueError`` with a descriptive message when validation fails.
    """
    if declared and declared not in SUPPORTED_IMAGE_TYPES:
        supported = ", ".join(sorted(SUPPORTED_IMAGE_TYPES))
        msg = f"Nicht unterstützter Dateityp: {declared}. Unterstützte Formate: {supported}"
        raise ValueError(msg)

    detected = detect_image_mime(header_bytes)
    if detected is None:
        msg = "Die Datei konnte nicht als unterstütztes Bildformat erkannt werden."
        raise ValueError(msg)

    if detected not in SUPPORTED_IMAGE_TYPES:
        supported = ", ".join(sorted(SUPPORTED_IMAGE_TYPES))
        msg = f"Nicht unterstützter Dateityp: {detected}. Unterstützte Formate: {supported}"
        raise ValueError(msg)

    return detected


def validate_image_size(size_bytes: int) -> None:
    """Raise ``ValueError`` if the image exceeds the maximum allowed size."""
    if size_bytes > MAX_IMAGE_SIZE_BYTES:
        max_mb = MAX_IMAGE_SIZE_BYTES // (1024 * 1024)
        msg = f"Datei ist zu groß ({size_bytes:,} Bytes). Maximum: {max_mb} MB."
        raise ValueError(msg)
