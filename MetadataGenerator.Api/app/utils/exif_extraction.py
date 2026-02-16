"""EXIF metadata extraction from image files.

Uses Pillow to extract common EXIF fields from images,
returning them as a flat dictionary.
"""

from __future__ import annotations

import io
import logging
from typing import Any

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

logger = logging.getLogger(__name__)

# EXIF fields we care about for metadata
_INTERESTING_TAGS: frozenset[str] = frozenset(
    {
        "Make",
        "Model",
        "DateTime",
        "DateTimeOriginal",
        "DateTimeDigitized",
        "ExposureTime",
        "FNumber",
        "ISOSpeedRatings",
        "FocalLength",
        "ImageWidth",
        "ImageLength",
        "ExifImageWidth",
        "ExifImageHeight",
        "GPSInfo",
        "Orientation",
        "Software",
        "LensModel",
        "LensMake",
        "WhiteBalance",
        "Flash",
    }
)


def _convert_gps_to_decimal(
    gps_data: dict[int | str, Any],
) -> dict[str, float | str | None]:
    """Convert GPS EXIF data to decimal lat/lon."""
    result: dict[str, float | str | None] = {}

    def _to_decimal(values: Any, ref: str) -> float | None:
        try:
            if hasattr(values, "__iter__"):
                vals = list(values)
            else:
                return None
            if len(vals) != 3:
                return None
            degrees = float(vals[0])
            minutes = float(vals[1])
            seconds = float(vals[2])
            decimal = degrees + minutes / 60.0 + seconds / 3600.0
            if ref in ("S", "W"):
                decimal = -decimal
            return round(decimal, 6)
        except (TypeError, ValueError, ZeroDivisionError):
            return None

    gps_decoded: dict[str, Any] = {}
    for key, val in gps_data.items():
        int_key = int(key) if isinstance(key, int) else None
        tag_name = GPSTAGS.get(int_key, str(key)) if int_key is not None else str(key)
        gps_decoded[tag_name] = val

    lat_ref = gps_decoded.get("GPSLatitudeRef", "N")
    lon_ref = gps_decoded.get("GPSLongitudeRef", "E")

    if "GPSLatitude" in gps_decoded:
        result["gps_latitude"] = _to_decimal(gps_decoded["GPSLatitude"], str(lat_ref))
    if "GPSLongitude" in gps_decoded:
        result["gps_longitude"] = _to_decimal(gps_decoded["GPSLongitude"], str(lon_ref))

    return result


def extract_exif(file_bytes: bytes) -> dict[str, str | float | None]:
    """Extract EXIF metadata from image bytes.

    Returns a flat dictionary of tag-name → value pairs.
    Returns an empty dict if no EXIF data is found or an error occurs.
    """
    result: dict[str, str | float | None] = {}

    try:
        img = Image.open(io.BytesIO(file_bytes))
    except Exception:
        logger.debug("Could not open image for EXIF extraction")
        return result

    # Image dimensions (always available)
    result["width"] = float(img.width)
    result["height"] = float(img.height)

    exif_data = img.getexif()
    if not exif_data:
        return result

    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, str(tag_id))

        if tag_name not in _INTERESTING_TAGS:
            continue

        if tag_name == "GPSInfo":
            # GPSInfo is a nested structure
            try:
                gps_ifd = exif_data.get_ifd(0x8825)
                if gps_ifd:
                    gps_dict: dict[int | str, Any] = dict(gps_ifd)  # type: ignore[arg-type]
                    gps = _convert_gps_to_decimal(gps_dict)
                    result.update(gps)
            except Exception:
                logger.debug("Failed to parse GPS data")
            continue

        # Convert IFD-rational and other types to simple values
        try:
            if isinstance(value, tuple) and len(value) == 2:
                # Rational number (numerator, denominator)
                result[tag_name] = float(value[0]) / float(value[1]) if value[1] else None
            elif isinstance(value, bytes):
                result[tag_name] = value.decode("utf-8", errors="replace")
            elif isinstance(value, (int, float)):
                result[tag_name] = float(value)
            else:
                result[tag_name] = str(value)
        except Exception:
            logger.debug("Failed to convert EXIF tag %s", tag_name)

    return result
