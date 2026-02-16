"""Tests for EXIF extraction edge cases and file validation branch coverage."""

from __future__ import annotations

import io

from PIL import Image
from PIL.ExifTags import Base

from app.utils.exif_extraction import extract_exif
from app.utils.file_validation import detect_image_mime, validate_image_content_type


class TestDetectImageMime:
    """Test magic-byte detection for various image formats."""

    def test_jpeg_magic(self) -> None:
        assert detect_image_mime(b"\xff\xd8\xff\xe0") == "image/jpeg"

    def test_png_magic(self) -> None:
        assert detect_image_mime(b"\x89PNG\r\n\x1a\n") == "image/png"

    def test_tiff_le_magic(self) -> None:
        assert detect_image_mime(b"II\x2a\x00") == "image/tiff"

    def test_tiff_be_magic(self) -> None:
        assert detect_image_mime(b"MM\x00\x2a") == "image/tiff"

    def test_webp_magic(self) -> None:
        header = b"RIFF\x00\x00\x00\x00WEBP"
        assert detect_image_mime(header) == "image/webp"

    def test_webp_riff_without_webp_marker(self) -> None:
        header = b"RIFF\x00\x00\x00\x00WAVE"
        assert detect_image_mime(header) is None

    def test_unknown_bytes(self) -> None:
        assert detect_image_mime(b"\x00\x00\x00\x00") is None


class TestValidateImageContentTypeEdge:
    """Edge cases for content-type validation."""

    def test_none_declared_with_valid_magic(self) -> None:
        jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 12
        mime = validate_image_content_type(None, jpeg)
        assert mime == "image/jpeg"


class TestExifEdgeCases:
    """Test EXIF extraction branches that may not be hit in normal cases."""

    def test_webp_has_dimensions(self) -> None:
        img = Image.new("RGB", (120, 80))
        buf = io.BytesIO()
        img.save(buf, format="WEBP")
        result = extract_exif(buf.getvalue())
        assert result["width"] == 120.0
        assert result["height"] == 80.0

    def test_jpeg_with_software_tag(self) -> None:
        img = Image.new("RGB", (10, 10))
        exif_data = img.getexif()
        exif_data[Base.Software] = "TestSoftware v1.0"
        buf = io.BytesIO()
        img.save(buf, format="JPEG", exif=exif_data.tobytes())
        result = extract_exif(buf.getvalue())
        assert result.get("Software") == "TestSoftware v1.0"

    def test_jpeg_with_datetime(self) -> None:
        img = Image.new("RGB", (10, 10))
        exif_data = img.getexif()
        exif_data[Base.DateTime] = "2024:01:15 10:30:00"
        buf = io.BytesIO()
        img.save(buf, format="JPEG", exif=exif_data.tobytes())
        result = extract_exif(buf.getvalue())
        assert result.get("DateTime") == "2024:01:15 10:30:00"

    def test_empty_bytes(self) -> None:
        result = extract_exif(b"")
        assert result == {}


class TestExifGpsExtraction:
    """Test GPS coordinate conversion from EXIF data."""

    def test_gps_conversion_helper(self) -> None:
        """Test the GPS conversion function directly."""
        from app.utils.exif_extraction import _convert_gps_to_decimal

        gps_data = {
            1: "N",  # GPSLatitudeRef
            2: (48.0, 52.0, 30.0),  # GPSLatitude
            3: "E",  # GPSLongitudeRef
            4: (8.0, 23.0, 15.0),  # GPSLongitude
        }
        result = _convert_gps_to_decimal(gps_data)
        assert "gps_latitude" in result
        assert "gps_longitude" in result
        assert result["gps_latitude"] is not None
        assert abs(result["gps_latitude"] - 48.875) < 0.01  # type: ignore[operator]

    def test_gps_south_west(self) -> None:
        from app.utils.exif_extraction import _convert_gps_to_decimal

        gps_data = {
            1: "S",
            2: (33.0, 51.0, 54.0),
            3: "W",
            4: (151.0, 12.0, 36.0),
        }
        result = _convert_gps_to_decimal(gps_data)
        assert result["gps_latitude"] is not None
        assert result["gps_latitude"] < 0  # type: ignore[operator]
        assert result["gps_longitude"] is not None
        assert result["gps_longitude"] < 0  # type: ignore[operator]

    def test_gps_invalid_values(self) -> None:
        from app.utils.exif_extraction import _convert_gps_to_decimal

        gps_data = {1: "N", 2: "invalid"}
        result = _convert_gps_to_decimal(gps_data)
        # Should handle gracefully
        assert isinstance(result, dict)


class TestContentUnderstandingKeywordFallback:
    """Test the keyword extraction fallback in the CU service."""

    def test_fallback_keywords_from_markdown(self) -> None:

        from app.services.content_understanding import AzureContentUnderstandingService

        svc = AzureContentUnderstandingService.__new__(AzureContentUnderstandingService)
        fields: dict[str, object] = {}
        markdown = "Dieses Bild zeigt einen wunderschönen Sonnenuntergang über dem Meer."
        keywords = svc._extract_keywords(fields, markdown)
        assert len(keywords) >= 3
        assert all(isinstance(k, str) for k in keywords)

    def test_fallback_keywords_empty_input(self) -> None:
        from app.services.content_understanding import AzureContentUnderstandingService

        svc = AzureContentUnderstandingService.__new__(AzureContentUnderstandingService)
        keywords = svc._extract_keywords(None, "")
        assert keywords == ["Allgemein", "Inhalt", "Medium"]

    def test_keywords_from_comma_string(self) -> None:
        from unittest.mock import MagicMock

        from app.services.content_understanding import AzureContentUnderstandingService

        svc = AzureContentUnderstandingService.__new__(AzureContentUnderstandingService)
        field = MagicMock()
        field.value = "Wald, Herbst, Natur, Bäume"
        fields = {"Keywords": field}
        keywords = svc._extract_keywords(fields, "")
        assert keywords == ["Wald", "Herbst", "Natur", "Bäume"]

    def test_keywords_from_list(self) -> None:
        from unittest.mock import MagicMock

        from app.services.content_understanding import AzureContentUnderstandingService

        svc = AzureContentUnderstandingService.__new__(AzureContentUnderstandingService)
        field = MagicMock()
        field.value = ["Alpha", "Beta", "Gamma"]
        fields = {"Keywords": field}
        keywords = svc._extract_keywords(fields, "")
        assert keywords == ["Alpha", "Beta", "Gamma"]

    def test_extract_field_missing(self) -> None:
        from app.services.content_understanding import AzureContentUnderstandingService

        svc = AzureContentUnderstandingService.__new__(AzureContentUnderstandingService)
        assert svc._extract_field(None, "Summary") == ""
        assert svc._extract_field({}, "Summary") == ""

    def test_extract_field_none_value(self) -> None:
        from unittest.mock import MagicMock

        from app.services.content_understanding import AzureContentUnderstandingService

        svc = AzureContentUnderstandingService.__new__(AzureContentUnderstandingService)
        field = MagicMock()
        field.value = None
        assert svc._extract_field({"Summary": field}, "Summary") == ""
