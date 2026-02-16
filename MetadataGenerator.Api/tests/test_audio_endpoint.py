"""Unit tests for audio metadata extraction endpoint."""

from __future__ import annotations

import struct
import wave
from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.dependencies import get_content_understanding_service, get_settings
from app.main import create_app
from app.models.analysis import AudioAnalysisResult
from app.utils.audio_utils import get_audio_duration, validate_audio_upload

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MOCK_AI_RESULT = AudioAnalysisResult(
    description=(
        "Ein Interview über aktuelle Technologietrends."
        " Die Gesprächsteilnehmer diskutieren künstliche Intelligenz."
    ),
    keywords=["Interview", "Technologie", "KI", "Innovation", "Zukunft"],
    summary="Interview über Technologietrends und künstliche Intelligenz.",
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
    svc.analyze_audio = AsyncMock(return_value=_MOCK_AI_RESULT)
    return svc


def _create_test_client() -> TestClient:
    app = create_app()
    mock_svc = _mock_cu_service()
    app.dependency_overrides[get_settings] = _test_settings
    app.dependency_overrides[get_content_understanding_service] = lambda: mock_svc
    return TestClient(app)


# ---------------------------------------------------------------------------
# Audio utility tests
# ---------------------------------------------------------------------------


class TestAudioUtils:
    """Tests for audio validation utilities."""

    def test_wav_duration(self) -> None:
        wav = _make_wav(duration_secs=2.0)
        dur = get_audio_duration(wav, "test.wav")
        assert dur is not None
        assert abs(dur - 2.0) < 1.0

    def test_invalid_bytes_returns_none(self) -> None:
        dur = get_audio_duration(b"not audio", "bad.mp3")
        assert dur is None

    def test_validate_unsupported_type(self) -> None:
        with pytest.raises(ValueError, match="Nicht unterstützter Audio-Dateityp"):
            validate_audio_upload("video/mp4", b"data", "video.mp4")

    def test_validate_too_long(self) -> None:
        # Mock a file that reports > 15 minutes
        with patch("app.utils.audio_utils.get_audio_duration", return_value=1000.0):
            with pytest.raises(ValueError, match="zu lang"):
                validate_audio_upload("audio/mpeg", b"data", "long.mp3")

    def test_validate_valid_audio(self) -> None:
        with patch("app.utils.audio_utils.get_audio_duration", return_value=30.0):
            mime, dur = validate_audio_upload("audio/mpeg", b"data", "ok.mp3")
            assert mime == "audio/mpeg"
            assert dur == 30.0


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------


class TestAnalyzeAudioEndpoint:
    """Tests for POST /api/v1/analyze/audio."""

    def test_valid_wav_returns_200(self) -> None:
        client = _create_test_client()
        wav = _make_wav()
        resp = client.post(
            "/api/v1/analyze/audio",
            files={"file": ("test.wav", wav, "audio/wav")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["file_name"] == "test.wav"
        assert body["mime_type"] == "audio/wav"
        assert body["description"] != ""
        assert len(body["keywords"]) >= 3
        assert body["summary"] != ""

    def test_valid_wav_x_wav_returns_200(self) -> None:
        client = _create_test_client()
        wav = _make_wav()
        resp = client.post(
            "/api/v1/analyze/audio",
            files={"file": ("test.wav", wav, "audio/x-wav")},
        )
        assert resp.status_code == 200

    def test_unsupported_type_returns_422(self) -> None:
        client = _create_test_client()
        resp = client.post(
            "/api/v1/analyze/audio",
            files={"file": ("test.txt", b"hello", "text/plain")},
        )
        assert resp.status_code == 422

    def test_too_long_audio_returns_422(self) -> None:
        """Audio exceeding 15 minutes should be rejected."""
        client = _create_test_client()
        wav = _make_wav(duration_secs=1.0)  # Short file but we mock duration

        with patch("app.utils.audio_utils.get_audio_duration", return_value=1000.0):
            resp = client.post(
                "/api/v1/analyze/audio",
                files={"file": ("long.wav", wav, "audio/wav")},
            )
        assert resp.status_code == 422
        assert "zu lang" in resp.json()["detail"]

    def test_processing_time_is_positive(self) -> None:
        client = _create_test_client()
        wav = _make_wav()
        resp = client.post(
            "/api/v1/analyze/audio",
            files={"file": ("test.wav", wav, "audio/wav")},
        )
        assert resp.status_code == 200
        assert resp.json()["processing_time_ms"] >= 0

    def test_keywords_between_3_and_15(self) -> None:
        client = _create_test_client()
        wav = _make_wav()
        resp = client.post(
            "/api/v1/analyze/audio",
            files={"file": ("test.wav", wav, "audio/wav")},
        )
        assert resp.status_code == 200
        kw = resp.json()["keywords"]
        assert 3 <= len(kw) <= 15

    def test_duration_returned(self) -> None:
        client = _create_test_client()
        wav = _make_wav(duration_secs=3.0)
        resp = client.post(
            "/api/v1/analyze/audio",
            files={"file": ("test.wav", wav, "audio/wav")},
        )
        assert resp.status_code == 200
        dur = resp.json()["duration_seconds"]
        assert dur is not None
        assert dur > 0

    def test_analysis_error_returns_500(self) -> None:
        from app.core.exceptions import AnalysisServiceError

        app = create_app()
        failing_svc = AsyncMock()
        failing_svc.analyze_audio = AsyncMock(
            side_effect=AnalysisServiceError(error_code="AZURE_HTTP_500", message="Internal error")
        )
        app.dependency_overrides[get_settings] = _test_settings
        app.dependency_overrides[get_content_understanding_service] = lambda: failing_svc
        client = TestClient(app)

        wav = _make_wav()
        resp = client.post(
            "/api/v1/analyze/audio",
            files={"file": ("test.wav", wav, "audio/wav")},
        )
        assert resp.status_code == 500
