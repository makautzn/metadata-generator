"""Unit tests for the production webhook endpoint."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.dependencies import get_content_understanding_service, get_settings
from app.main import create_app
from app.models.analysis import AudioAnalysisResult, ImageAnalysisResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_IMG_AI = ImageAnalysisResult(
    description="Ein Bild einer Berglandschaft. Die Berge sind schneebedeckt.",
    keywords=["Berge", "Landschaft", "Schnee"],
    caption="Schneebedeckte Berglandschaft.",
)

_AUDIO_AI = AudioAnalysisResult(
    description="Ein Interview über Umweltschutz. Die Sprecher betonen Nachhaltigkeit.",
    keywords=["Umwelt", "Nachhaltigkeit", "Interview"],
    summary="Interview über Nachhaltigkeit und Umweltschutz.",
)

_VALID_API_KEY = "test-webhook-key-123"


def _test_settings() -> Settings:
    return Settings(
        app_name="Test API",
        environment="testing",
        debug=True,
        allowed_origins=["http://testserver"],
        azure_content_understanding_endpoint="https://test.azure.com",
        azure_content_understanding_key="test-key",
        webhook_api_keys=[_VALID_API_KEY],
    )


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


def _valid_body(files: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "files": files
        or [
            {
                "url": "https://example.com/photo.jpg",
                "file_type": "image",
                "reference_id": "ref-1",
            }
        ],
        "callback_url": "https://example.com/callback",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestWebhookAuth:
    """Authentication tests for POST /api/v1/webhook/analyze."""

    def test_missing_api_key_returns_401(self) -> None:
        resp = _client().post("/api/v1/webhook/analyze", json=_valid_body())
        assert resp.status_code == 401

    def test_invalid_api_key_returns_401(self) -> None:
        resp = _client().post(
            "/api/v1/webhook/analyze",
            json=_valid_body(),
            headers={"X-API-Key": "wrong-key"},
        )
        assert resp.status_code == 401

    def test_valid_api_key_returns_202(self) -> None:
        resp = _client().post(
            "/api/v1/webhook/analyze",
            json=_valid_body(),
            headers={"X-API-Key": _VALID_API_KEY},
        )
        assert resp.status_code == 202


class TestWebhookValidation:
    """Request validation tests."""

    def test_empty_files_returns_422(self) -> None:
        body = {"files": [], "callback_url": "https://example.com/cb"}
        resp = _client().post(
            "/api/v1/webhook/analyze",
            json=body,
            headers={"X-API-Key": _VALID_API_KEY},
        )
        assert resp.status_code == 422

    def test_invalid_callback_url_returns_422(self) -> None:
        body = {
            "files": [{"url": "https://example.com/img.jpg", "file_type": "image"}],
            "callback_url": "not-a-url",
        }
        resp = _client().post(
            "/api/v1/webhook/analyze",
            json=body,
            headers={"X-API-Key": _VALID_API_KEY},
        )
        assert resp.status_code == 422


class TestWebhookAccepted:
    """Tests for the 202 response."""

    def test_response_contains_job_id(self) -> None:
        resp = _client().post(
            "/api/v1/webhook/analyze",
            json=_valid_body(),
            headers={"X-API-Key": _VALID_API_KEY},
        )
        body = resp.json()
        assert "job_id" in body
        assert body["job_id"] != ""

    def test_job_id_is_unique(self) -> None:
        client = _client()
        ids = set()
        for _ in range(5):
            resp = client.post(
                "/api/v1/webhook/analyze",
                json=_valid_body(),
                headers={"X-API-Key": _VALID_API_KEY},
            )
            ids.add(resp.json()["job_id"])
        assert len(ids) == 5

    def test_total_files_matches(self) -> None:
        files = [{"url": f"https://example.com/f{i}.jpg", "file_type": "image"} for i in range(3)]
        resp = _client().post(
            "/api/v1/webhook/analyze",
            json=_valid_body(files),
            headers={"X-API-Key": _VALID_API_KEY},
        )
        assert resp.json()["total_files"] == 3


class TestWebhookBackgroundProcessing:
    """Tests for background job execution."""

    def test_callback_is_posted(self) -> None:
        """Verify the background task downloads files and POSTs to callback URL."""
        import asyncio

        from app.routers.webhook import WebhookRequest, _run_webhook_job

        req = WebhookRequest(**_valid_body())
        svc = _mock_cu_service()

        # Mock _download_file to return fake image bytes
        fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        captured_payload: dict[str, Any] = {}

        async def _mock_download(url: str) -> tuple[bytes, str]:
            return fake_jpeg, "image/jpeg"

        async def _mock_post(self: Any, url: str, **kwargs: Any) -> Any:
            captured_payload.update(kwargs.get("json", {}))
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.raise_for_status = lambda: None
            return mock_resp

        with (
            patch("app.routers.webhook._download_file", side_effect=_mock_download),
            patch("httpx.AsyncClient.post", new=_mock_post),
        ):
            asyncio.get_event_loop().run_until_complete(_run_webhook_job("test-job-1", req, svc))

        assert captured_payload["job_id"] == "test-job-1"
        assert captured_payload["status"] == "completed"
        assert captured_payload["total_files"] == 1
        assert captured_payload["successful"] == 1

    def test_download_failure_produces_per_file_error(self) -> None:
        import asyncio

        from app.routers.webhook import WebhookRequest, _run_webhook_job

        req = WebhookRequest(**_valid_body())
        svc = _mock_cu_service()

        captured: dict[str, Any] = {}

        async def _fail_download(url: str) -> tuple[bytes, str]:
            msg = "Connection refused"
            raise ConnectionError(msg)

        async def _mock_post(self: Any, url: str, **kwargs: Any) -> Any:
            captured.update(kwargs.get("json", {}))
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.raise_for_status = lambda: None
            return mock_resp

        with (
            patch("app.routers.webhook._download_file", side_effect=_fail_download),
            patch("httpx.AsyncClient.post", new=_mock_post),
        ):
            asyncio.get_event_loop().run_until_complete(_run_webhook_job("test-job-2", req, svc))

        assert captured["status"] == "failed"
        assert captured["failed"] == 1
        result = captured["results"][0]
        assert result["status"] == "error"
        assert "Download" in result["error"]["detail"]

    def test_callback_payload_schema(self) -> None:
        """Verify callback payload matches documented schema."""
        import asyncio

        from app.routers.webhook import WebhookRequest, _run_webhook_job

        files = [
            {"url": "https://example.com/a.jpg", "file_type": "image", "reference_id": "r1"},
            {"url": "https://example.com/b.mp3", "file_type": "audio", "reference_id": "r2"},
        ]
        req = WebhookRequest(**_valid_body(files))
        svc = _mock_cu_service()

        fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        captured: dict[str, Any] = {}

        async def _mock_download(url: str) -> tuple[bytes, str]:
            if "mp3" in url:
                return b"\x00" * 100, "audio/mpeg"
            return fake_jpeg, "image/jpeg"

        async def _mock_post(self: Any, url: str, **kwargs: Any) -> Any:
            captured.update(kwargs.get("json", {}))
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.raise_for_status = lambda: None
            return mock_resp

        with (
            patch("app.routers.webhook._download_file", side_effect=_mock_download),
            patch("httpx.AsyncClient.post", new=_mock_post),
        ):
            asyncio.get_event_loop().run_until_complete(_run_webhook_job("test-job-3", req, svc))

        assert "job_id" in captured
        assert "status" in captured
        assert "results" in captured
        assert "total_files" in captured
        assert "successful" in captured
        assert "failed" in captured
        assert "processing_time_ms" in captured
        assert len(captured["results"]) == 2
