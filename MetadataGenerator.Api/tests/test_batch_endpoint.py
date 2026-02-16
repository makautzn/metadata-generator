"""Unit tests for batch file analysis endpoint."""

from __future__ import annotations

import struct
import wave
from io import BytesIO
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.dependencies import get_content_understanding_service, get_settings
from app.core.exceptions import AnalysisServiceError
from app.main import create_app
from app.models.analysis import AudioAnalysisResult, ImageAnalysisResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_IMG_AI = ImageAnalysisResult(
    description="Ein Foto eines Gebäudes. Es zeigt moderne Architektur.",
    keywords=["Architektur", "Gebäude", "Modern"],
    caption="Modernes Gebäude bei Tageslicht.",
)

_AUDIO_AI = AudioAnalysisResult(
    description="Ein Interview über aktuelle Trends. Die Sprecher diskutieren Technologie.",
    keywords=["Interview", "Technologie", "Trends"],
    summary="Interview über Technologietrends.",
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


def _make_jpeg(size: int = 128) -> bytes:
    """Minimal valid JPEG bytes."""
    header = b"\xff\xd8\xff\xe0"
    return header + b"\x00" * max(0, size - len(header))


def _make_png() -> bytes:
    """Minimal valid PNG magic bytes."""
    header = b"\x89PNG\r\n\x1a\n"
    return header + b"\x00" * 100


def _make_wav(duration_secs: float = 1.0, sample_rate: int = 8000) -> bytes:
    """Create a minimal WAV file in memory."""
    buf = BytesIO()
    n_frames = int(sample_rate * duration_secs)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{n_frames}h", *([0] * n_frames)))
    return buf.getvalue()


def _mock_cu_service() -> AsyncMock:
    svc = AsyncMock()
    svc.analyze_image = AsyncMock(return_value=_IMG_AI)
    svc.analyze_audio = AsyncMock(return_value=_AUDIO_AI)
    return svc


def _client(cu_svc: AsyncMock | None = None) -> TestClient:
    app = create_app()
    svc = cu_svc or _mock_cu_service()
    app.dependency_overrides[get_settings] = _test_settings
    app.dependency_overrides[get_content_understanding_service] = lambda: svc
    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestBatchEndpoint:
    """Tests for POST /api/v1/analyze/batch."""

    # -- success scenarios -------------------------------------------------

    def test_three_images_returns_three_results(self) -> None:
        client = _client()
        files = [("files", (f"img{i}.jpg", _make_jpeg(), "image/jpeg")) for i in range(3)]
        resp = client.post("/api/v1/analyze/batch", files=files)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_files"] == 3
        assert body["successful"] == 3
        assert body["failed"] == 0
        assert len(body["results"]) == 3

    def test_two_audio_files_return_two_results(self) -> None:
        client = _client()
        files = [
            ("files", ("a.wav", _make_wav(), "audio/wav")),
            ("files", ("b.wav", _make_wav(), "audio/wav")),
        ]
        resp = client.post("/api/v1/analyze/batch", files=files)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_files"] == 2
        assert body["successful"] == 2

    def test_mixed_batch_correct_file_types(self) -> None:
        client = _client()
        files = [
            ("files", ("photo.jpg", _make_jpeg(), "image/jpeg")),
            ("files", ("clip.wav", _make_wav(), "audio/wav")),
            ("files", ("photo2.png", _make_png(), "image/png")),
        ]
        resp = client.post("/api/v1/analyze/batch", files=files)
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert results[0]["file_type"] == "image"
        assert results[1]["file_type"] == "audio"
        assert results[2]["file_type"] == "image"

    def test_results_preserve_upload_order(self) -> None:
        client = _client()
        files = [("files", (f"file_{i}.jpg", _make_jpeg(), "image/jpeg")) for i in range(5)]
        resp = client.post("/api/v1/analyze/batch", files=files)
        results = resp.json()["results"]
        for i, r in enumerate(results):
            assert r["file_index"] == i
            assert r["file_name"] == f"file_{i}.jpg"

    # -- partial failure ---------------------------------------------------

    def test_invalid_file_produces_error_without_failing_batch(self) -> None:
        client = _client()
        files = [
            ("files", ("good.jpg", _make_jpeg(), "image/jpeg")),
            ("files", ("bad.txt", b"hello", "text/plain")),
            ("files", ("ok.wav", _make_wav(), "audio/wav")),
        ]
        resp = client.post("/api/v1/analyze/batch", files=files)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_files"] == 3
        assert body["successful"] == 2
        assert body["failed"] == 1
        err_result = body["results"][1]
        assert err_result["status"] == "error"
        assert err_result["file_type"] == "unknown"

    def test_analysis_error_does_not_fail_batch(self) -> None:
        svc = _mock_cu_service()
        call_count = 0

        async def _side_effect(*args: object, **kwargs: object) -> ImageAnalysisResult:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise AnalysisServiceError("AZURE_500", "Internal error")
            return _IMG_AI

        svc.analyze_image = AsyncMock(side_effect=_side_effect)
        client = _client(svc)
        files = [("files", (f"img{i}.jpg", _make_jpeg(), "image/jpeg")) for i in range(3)]
        resp = client.post("/api/v1/analyze/batch", files=files)
        assert resp.status_code == 200
        body = resp.json()
        assert body["successful"] == 2
        assert body["failed"] == 1

    # -- validation errors -------------------------------------------------

    def test_more_than_20_files_returns_422(self) -> None:
        client = _client()
        files = [("files", (f"img{i}.jpg", _make_jpeg(), "image/jpeg")) for i in range(21)]
        resp = client.post("/api/v1/analyze/batch", files=files)
        assert resp.status_code == 422

    def test_empty_batch_returns_422(self) -> None:
        client = _client()
        resp = client.post("/api/v1/analyze/batch", files=[])
        assert resp.status_code == 422

    # -- counts -----------------------------------------------------------

    def test_summary_counts_are_accurate(self) -> None:
        client = _client()
        files = [
            ("files", ("good.jpg", _make_jpeg(), "image/jpeg")),
            ("files", ("bad.txt", b"nope", "text/plain")),
        ]
        resp = client.post("/api/v1/analyze/batch", files=files)
        body = resp.json()
        assert body["total_files"] == 2
        assert body["successful"] == 1
        assert body["failed"] == 1

    # -- processing time ---------------------------------------------------

    def test_total_processing_time_is_positive(self) -> None:
        client = _client()
        files = [("files", ("x.jpg", _make_jpeg(), "image/jpeg"))]
        resp = client.post("/api/v1/analyze/batch", files=files)
        assert resp.json()["total_processing_time_ms"] >= 0

    # -- image metadata fields populated -----------------------------------

    def test_image_result_has_metadata(self) -> None:
        client = _client()
        files = [("files", ("pic.jpg", _make_jpeg(), "image/jpeg"))]
        resp = client.post("/api/v1/analyze/batch", files=files)
        result = resp.json()["results"][0]
        assert result["status"] == "success"
        meta = result["metadata"]
        assert meta["description"] != ""
        assert len(meta["keywords"]) >= 3
        assert meta["caption"] != ""

    # -- audio metadata fields populated -----------------------------------

    def test_audio_result_has_metadata(self) -> None:
        client = _client()
        files = [("files", ("clip.wav", _make_wav(), "audio/wav"))]
        resp = client.post("/api/v1/analyze/batch", files=files)
        result = resp.json()["results"][0]
        assert result["status"] == "success"
        meta = result["metadata"]
        assert meta["description"] != ""
        assert len(meta["keywords"]) >= 3
        assert meta["summary"] != ""
