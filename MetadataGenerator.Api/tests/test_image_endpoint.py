"""Unit tests for image metadata extraction endpoint and utilities."""

from __future__ import annotations

import io
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import Settings
from app.core.dependencies import get_content_understanding_service, get_settings
from app.main import create_app
from app.models.analysis import ImageAnalysisResult
from app.utils.exif_extraction import extract_exif
from app.utils.file_validation import (
    MAX_IMAGE_SIZE_BYTES,
    validate_image_content_type,
    validate_image_size,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MOCK_AI_RESULT = ImageAnalysisResult(
    description=(
        "Ein Foto eines historischen Gebäudes in der Innenstadt."
        " Das Gebäude stammt aus der Barockzeit."
    ),
    keywords=["Gebäude", "Architektur", "Barock", "Stadt", "Geschichte"],
    caption="Historisches Barockgebäude im Stadtzentrum.",
)


def _test_settings() -> Settings:
    return Settings(
        app_name="Test API",
        environment="testing",
        debug=True,
        allowed_origins=["http://testserver"],
        azure_content_understanding_endpoint="https://test.azure.com",
        azure_content_understanding_key="test-key",
    )


def _make_jpeg(width: int = 100, height: int = 100) -> bytes:
    """Create a minimal JPEG image in memory."""
    img = Image.new("RGB", (width, height), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_png(width: int = 100, height: int = 100) -> bytes:
    """Create a minimal PNG image in memory."""
    img = Image.new("RGB", (width, height), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_webp(width: int = 100, height: int = 100) -> bytes:
    """Create a minimal WebP image in memory."""
    img = Image.new("RGB", (width, height), color="green")
    buf = io.BytesIO()
    img.save(buf, format="WEBP")
    return buf.getvalue()


def _make_tiff(width: int = 100, height: int = 100) -> bytes:
    """Create a minimal TIFF image in memory."""
    img = Image.new("RGB", (width, height), color="yellow")
    buf = io.BytesIO()
    img.save(buf, format="TIFF")
    return buf.getvalue()


def _mock_cu_service() -> AsyncMock:
    svc = AsyncMock()
    svc.analyze_image = AsyncMock(return_value=_MOCK_AI_RESULT)
    return svc


def _create_test_client() -> TestClient:
    app = create_app()
    mock_svc = _mock_cu_service()
    app.dependency_overrides[get_settings] = _test_settings
    app.dependency_overrides[get_content_understanding_service] = lambda: mock_svc
    return TestClient(app)


# ---------------------------------------------------------------------------
# File validation tests
# ---------------------------------------------------------------------------


class TestFileValidation:
    """Tests for file validation utilities."""

    def test_validate_jpeg_content_type(self) -> None:
        jpeg_bytes = _make_jpeg()
        mime = validate_image_content_type("image/jpeg", jpeg_bytes[:16])
        assert mime == "image/jpeg"

    def test_validate_png_content_type(self) -> None:
        png_bytes = _make_png()
        mime = validate_image_content_type("image/png", png_bytes[:16])
        assert mime == "image/png"

    def test_validate_webp_content_type(self) -> None:
        webp_bytes = _make_webp()
        mime = validate_image_content_type("image/webp", webp_bytes[:16])
        assert mime == "image/webp"

    def test_validate_tiff_content_type(self) -> None:
        tiff_bytes = _make_tiff()
        mime = validate_image_content_type("image/tiff", tiff_bytes[:16])
        assert mime == "image/tiff"

    def test_unsupported_declared_type_rejected(self) -> None:
        with pytest.raises(ValueError, match="Nicht unterstützter Dateityp"):
            validate_image_content_type("application/pdf", b"\x00" * 16)

    def test_unrecognised_magic_bytes_rejected(self) -> None:
        with pytest.raises(ValueError, match="nicht als unterstütztes Bildformat"):
            validate_image_content_type(None, b"\x00" * 16)

    def test_size_within_limit(self) -> None:
        validate_image_size(MAX_IMAGE_SIZE_BYTES)  # exactly at limit — OK

    def test_size_exceeds_limit(self) -> None:
        with pytest.raises(ValueError, match="zu groß"):
            validate_image_size(MAX_IMAGE_SIZE_BYTES + 1)


# ---------------------------------------------------------------------------
# EXIF extraction tests
# ---------------------------------------------------------------------------


class TestExifExtraction:
    """Tests for EXIF metadata extraction."""

    def test_jpeg_has_dimensions(self) -> None:
        data = _make_jpeg(200, 150)
        exif = extract_exif(data)
        assert exif["width"] == 200.0
        assert exif["height"] == 150.0

    def test_png_without_exif(self) -> None:
        data = _make_png()
        exif = extract_exif(data)
        # Should still have dimensions but no camera fields
        assert "width" in exif
        assert "Make" not in exif

    def test_invalid_bytes_returns_empty(self) -> None:
        exif = extract_exif(b"not an image")
        assert exif == {}

    def test_jpeg_with_exif_data(self) -> None:
        """Create a JPEG with synthetic EXIF and verify extraction."""
        from PIL.ExifTags import Base

        img = Image.new("RGB", (100, 100), color="red")
        exif_data = img.getexif()
        exif_data[Base.Make] = "TestCamera"
        exif_data[Base.Model] = "Model X"
        buf = io.BytesIO()
        img.save(buf, format="JPEG", exif=exif_data.tobytes())
        result = extract_exif(buf.getvalue())
        assert result.get("Make") == "TestCamera"
        assert result.get("Model") == "Model X"

    def test_exif_with_numeric_values(self) -> None:
        """EXIF numeric fields are extracted as floats."""
        from PIL.ExifTags import Base

        img = Image.new("RGB", (50, 50))
        exif_data = img.getexif()
        exif_data[Base.Orientation] = 1
        buf = io.BytesIO()
        img.save(buf, format="JPEG", exif=exif_data.tobytes())
        result = extract_exif(buf.getvalue())
        assert result.get("Orientation") == 1.0

    def test_tiff_dimensions(self) -> None:
        data = _make_tiff(300, 200)
        exif = extract_exif(data)
        assert exif["width"] == 300.0
        assert exif["height"] == 200.0


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------


class TestAnalyzeImageEndpoint:
    """Tests for POST /api/v1/analyze/image."""

    def test_valid_jpeg_returns_200(self) -> None:
        client = _create_test_client()
        jpeg = _make_jpeg()
        resp = client.post(
            "/api/v1/analyze/image",
            files={"file": ("test.jpg", jpeg, "image/jpeg")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["file_name"] == "test.jpg"
        assert body["mime_type"] == "image/jpeg"
        assert body["description"] != ""
        assert len(body["keywords"]) >= 3
        assert body["caption"] != ""

    def test_valid_png_returns_200(self) -> None:
        client = _create_test_client()
        png = _make_png()
        resp = client.post(
            "/api/v1/analyze/image",
            files={"file": ("test.png", png, "image/png")},
        )
        assert resp.status_code == 200
        assert resp.json()["mime_type"] == "image/png"

    def test_valid_webp_returns_200(self) -> None:
        client = _create_test_client()
        webp = _make_webp()
        resp = client.post(
            "/api/v1/analyze/image",
            files={"file": ("test.webp", webp, "image/webp")},
        )
        assert resp.status_code == 200
        assert resp.json()["mime_type"] == "image/webp"

    def test_oversized_file_returns_413(self) -> None:
        client = _create_test_client()
        # Create a "file" that exceeds 10 MB (header only — validation happens on length)
        big_data = b"\xff\xd8\xff" + b"\x00" * (MAX_IMAGE_SIZE_BYTES + 1)
        resp = client.post(
            "/api/v1/analyze/image",
            files={"file": ("big.jpg", big_data, "image/jpeg")},
        )
        assert resp.status_code == 413

    def test_unsupported_type_returns_422(self) -> None:
        client = _create_test_client()
        resp = client.post(
            "/api/v1/analyze/image",
            files={"file": ("doc.pdf", b"%PDF-1.4", "application/pdf")},
        )
        assert resp.status_code == 422

    def test_processing_time_is_positive(self) -> None:
        client = _create_test_client()
        jpeg = _make_jpeg()
        resp = client.post(
            "/api/v1/analyze/image",
            files={"file": ("test.jpg", jpeg, "image/jpeg")},
        )
        assert resp.status_code == 200
        assert resp.json()["processing_time_ms"] >= 0

    def test_exif_populated_when_available(self) -> None:
        from PIL.ExifTags import Base

        img = Image.new("RGB", (100, 100))
        exif_data = img.getexif()
        exif_data[Base.Make] = "Nikon"
        buf = io.BytesIO()
        img.save(buf, format="JPEG", exif=exif_data.tobytes())

        client = _create_test_client()
        resp = client.post(
            "/api/v1/analyze/image",
            files={"file": ("cam.jpg", buf.getvalue(), "image/jpeg")},
        )
        assert resp.status_code == 200
        assert resp.json()["exif"].get("Make") == "Nikon"

    def test_image_without_exif_returns_empty_exif(self) -> None:
        client = _create_test_client()
        png = _make_png()
        resp = client.post(
            "/api/v1/analyze/image",
            files={"file": ("no_exif.png", png, "image/png")},
        )
        assert resp.status_code == 200
        exif = resp.json()["exif"]
        # Should have dimensions but no camera fields
        assert "Make" not in exif

    def test_keywords_count_between_3_and_15(self) -> None:
        client = _create_test_client()
        jpeg = _make_jpeg()
        resp = client.post(
            "/api/v1/analyze/image",
            files={"file": ("test.jpg", jpeg, "image/jpeg")},
        )
        assert resp.status_code == 200
        kw = resp.json()["keywords"]
        assert 3 <= len(kw) <= 15

    def test_analysis_error_returns_500(self) -> None:
        from app.core.exceptions import AnalysisServiceError

        app = create_app()
        failing_svc = AsyncMock()
        failing_svc.analyze_image = AsyncMock(
            side_effect=AnalysisServiceError(error_code="AZURE_HTTP_500", message="Internal error")
        )
        app.dependency_overrides[get_settings] = _test_settings
        app.dependency_overrides[get_content_understanding_service] = lambda: failing_svc
        client = TestClient(app)

        jpeg = _make_jpeg()
        resp = client.post(
            "/api/v1/analyze/image",
            files={"file": ("err.jpg", jpeg, "image/jpeg")},
        )
        assert resp.status_code == 500
