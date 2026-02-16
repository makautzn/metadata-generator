"""Unit tests for the Azure Content Understanding integration service."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import (
    AnalysisServiceError,
    ConfigurationError,
    TransientError,
)
from app.models.analysis import AudioAnalysisResult, ImageAnalysisResult
from app.services.content_understanding import (
    AzureContentUnderstandingService,
    ContentUnderstandingServiceProtocol,
)

# ---------------------------------------------------------------------------
# Helpers — build fake Azure SDK objects
# ---------------------------------------------------------------------------


def _make_content_field(value: Any) -> MagicMock:
    """Create a mock ``ContentField`` with a ``.value`` attribute."""
    field = MagicMock()
    field.value = value
    return field


def _make_media_content(
    *,
    markdown: str = "Some content",
    description: str = "Eine Beschreibung",
    summary: str | None = None,
    caption: str | None = None,
    keywords: list[str] | None = None,
) -> MagicMock:
    """Build a mock ``MediaContent`` returned by the SDK."""
    fields: dict[str, Any] = {
        "Description": _make_content_field(description),
    }
    if summary is not None:
        fields["Summary"] = _make_content_field(summary)
    if caption is not None:
        fields["Caption"] = _make_content_field(caption)
    if keywords is not None:
        fields["Keywords"] = _make_content_field(keywords)

    content = MagicMock()
    content.markdown = markdown
    content.fields = fields
    return content


def _make_analyze_result(contents: list[MagicMock] | None = None) -> MagicMock:
    """Build a mock ``AnalyzeResult``."""
    result = MagicMock()
    result.contents = contents or []
    return result


def _build_service(
    endpoint: str = "https://test.cognitiveservices.azure.com",
    key: str = "test-key-12345",
    max_retries: int = 3,
) -> AzureContentUnderstandingService:
    return AzureContentUnderstandingService(
        endpoint=endpoint,
        key=key,
        max_retries=max_retries,
    )


# ---------------------------------------------------------------------------
# Configuration tests
# ---------------------------------------------------------------------------


class TestConfiguration:
    """Tests for service initialisation and configuration validation."""

    def test_missing_endpoint_raises(self) -> None:
        with pytest.raises(ConfigurationError) as exc_info:
            AzureContentUnderstandingService(endpoint="", key="some-key")
        assert exc_info.value.error_code == "MISSING_CONFIG"

    def test_missing_key_raises(self) -> None:
        with pytest.raises(ConfigurationError) as exc_info:
            AzureContentUnderstandingService(endpoint="https://test.azure.com", key="")
        assert exc_info.value.error_code == "MISSING_CONFIG"

    def test_valid_config_creates_service(self) -> None:
        service = _build_service()
        assert isinstance(service, ContentUnderstandingServiceProtocol)


# ---------------------------------------------------------------------------
# Image analysis tests
# ---------------------------------------------------------------------------


class TestAnalyzeImage:
    """Tests for analyse_image()."""

    @pytest.mark.asyncio
    async def test_returns_populated_result(self) -> None:
        content = _make_media_content(
            description="Ein Foto eines Waldes",
            caption="Wald im Herbst",
            keywords=["Wald", "Herbst", "Natur", "Bäume"],
        )
        analyze_result = _make_analyze_result([content])

        service = _build_service()
        mock_poller = AsyncMock()
        mock_poller.result.return_value = analyze_result

        mock_client = AsyncMock()
        mock_client.begin_analyze_binary.return_value = mock_poller
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(service, "_create_client", return_value=mock_client):
            result = await service.analyze_image(b"fake-image-data", "image/jpeg")

        assert isinstance(result, ImageAnalysisResult)
        assert result.description == "Ein Foto eines Waldes"
        assert result.caption == "Wald im Herbst"
        assert result.keywords == ["Wald", "Herbst", "Natur", "Bäume"]

    @pytest.mark.asyncio
    async def test_fields_non_empty(self) -> None:
        content = _make_media_content(
            description="Beschreibung",
            caption="Bildunterschrift",
            keywords=["Eins", "Zwei", "Drei"],
        )
        analyze_result = _make_analyze_result([content])

        service = _build_service()
        mock_poller = AsyncMock()
        mock_poller.result.return_value = analyze_result

        mock_client = AsyncMock()
        mock_client.begin_analyze_binary.return_value = mock_poller
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(service, "_create_client", return_value=mock_client):
            result = await service.analyze_image(b"data", "image/png")

        assert result.description != ""
        assert result.caption != ""
        assert all(k != "" for k in result.keywords)

    @pytest.mark.asyncio
    async def test_keywords_count_between_3_and_15(self) -> None:
        content = _make_media_content(
            description="Foto",
            caption="Bild",
            keywords=["A", "B", "C", "D", "E"],
        )
        analyze_result = _make_analyze_result([content])

        service = _build_service()
        mock_poller = AsyncMock()
        mock_poller.result.return_value = analyze_result

        mock_client = AsyncMock()
        mock_client.begin_analyze_binary.return_value = mock_poller
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(service, "_create_client", return_value=mock_client):
            result = await service.analyze_image(b"data", "image/jpeg")

        assert 3 <= len(result.keywords) <= 15

    @pytest.mark.asyncio
    async def test_empty_result_raises(self) -> None:
        analyze_result = _make_analyze_result([])

        service = _build_service()
        mock_poller = AsyncMock()
        mock_poller.result.return_value = analyze_result

        mock_client = AsyncMock()
        mock_client.begin_analyze_binary.return_value = mock_poller
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(service, "_create_client", return_value=mock_client):
            with pytest.raises(AnalysisServiceError) as exc_info:
                await service.analyze_image(b"data", "image/jpeg")
            assert exc_info.value.error_code == "EMPTY_RESULT"


# ---------------------------------------------------------------------------
# Audio analysis tests
# ---------------------------------------------------------------------------


class TestAnalyzeAudio:
    """Tests for analyse_audio()."""

    @pytest.mark.asyncio
    async def test_returns_populated_result(self) -> None:
        content = _make_media_content(
            description="Ein Interview über Technologie",
            summary="Zusammenfassung des Interviews",
            keywords=["Interview", "Technologie", "Innovation"],
            markdown="Interview Transkript hier",
        )
        analyze_result = _make_analyze_result([content])

        service = _build_service()
        mock_poller = AsyncMock()
        mock_poller.result.return_value = analyze_result

        mock_client = AsyncMock()
        mock_client.begin_analyze_binary.return_value = mock_poller
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(service, "_create_client", return_value=mock_client):
            result = await service.analyze_audio(b"fake-audio", "audio/mpeg")

        assert isinstance(result, AudioAnalysisResult)
        assert result.description == "Ein Interview über Technologie"
        assert result.summary == "Zusammenfassung des Interviews"
        assert result.keywords == ["Interview", "Technologie", "Innovation"]

    @pytest.mark.asyncio
    async def test_fields_non_empty(self) -> None:
        content = _make_media_content(
            description="Audio",
            summary="Audio Zusammenfassung",
            keywords=["A", "B", "C"],
        )
        analyze_result = _make_analyze_result([content])

        service = _build_service()
        mock_poller = AsyncMock()
        mock_poller.result.return_value = analyze_result

        mock_client = AsyncMock()
        mock_client.begin_analyze_binary.return_value = mock_poller
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(service, "_create_client", return_value=mock_client):
            result = await service.analyze_audio(b"data", "audio/wav")

        assert result.description != ""
        assert result.summary != ""
        assert all(k != "" for k in result.keywords)


# ---------------------------------------------------------------------------
# Retry logic tests
# ---------------------------------------------------------------------------


class TestRetryLogic:
    """Tests for exponential-backoff retry on transient errors."""

    @pytest.mark.asyncio
    async def test_retry_on_429_succeeds_on_second_attempt(self) -> None:
        from azure.core.exceptions import HttpResponseError

        content = _make_media_content(
            description="Erfolg nach Retry",
            caption="Bild",
            keywords=["Retry", "Erfolg", "Test"],
        )
        analyze_result = _make_analyze_result([content])

        # First call raises 429, second succeeds
        error_429 = HttpResponseError(message="Rate limited")
        error_429.status_code = 429

        service = _build_service(max_retries=3)
        mock_poller = AsyncMock()
        mock_poller.result.return_value = analyze_result

        mock_client = AsyncMock()
        mock_client.begin_analyze_binary.side_effect = [error_429, mock_poller]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.object(service, "_create_client", return_value=mock_client),
            patch("app.services.content_understanding.asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await service.analyze_image(b"data", "image/jpeg")

        assert isinstance(result, ImageAnalysisResult)
        assert result.description == "Erfolg nach Retry"

    @pytest.mark.asyncio
    async def test_retry_exhaustion_raises_transient_error(self) -> None:
        from azure.core.exceptions import HttpResponseError

        error_503 = HttpResponseError(message="Service unavailable")
        error_503.status_code = 503

        service = _build_service(max_retries=2)

        mock_client = AsyncMock()
        mock_client.begin_analyze_binary.side_effect = error_503
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.object(service, "_create_client", return_value=mock_client),
            patch("app.services.content_understanding.asyncio.sleep", new_callable=AsyncMock),
        ):
            with pytest.raises(TransientError) as exc_info:
                await service.analyze_image(b"data", "image/jpeg")
            assert exc_info.value.error_code == "MAX_RETRIES_EXCEEDED"

    @pytest.mark.asyncio
    async def test_non_retryable_error_raises_immediately(self) -> None:
        from azure.core.exceptions import HttpResponseError

        error_400 = HttpResponseError(message="Bad request")
        error_400.status_code = 400

        service = _build_service(max_retries=3)

        mock_client = AsyncMock()
        mock_client.begin_analyze_binary.side_effect = error_400
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(service, "_create_client", return_value=mock_client):
            with pytest.raises(AnalysisServiceError) as exc_info:
                await service.analyze_image(b"data", "image/jpeg")
            assert exc_info.value.error_code == "AZURE_HTTP_400"

        # Should have been called only once (no retries)
        assert mock_client.begin_analyze_binary.call_count == 1


# ---------------------------------------------------------------------------
# Dependency injection integration test
# ---------------------------------------------------------------------------


class TestDependencyInjection:
    """Test that the service can be resolved from FastAPI DI."""

    def test_service_resolvable_from_di(self) -> None:
        from unittest.mock import patch as mock_patch

        from app.core.config import Settings
        from app.core.dependencies import get_content_understanding_service

        test_settings = Settings(
            azure_content_understanding_endpoint="https://test.cognitiveservices.azure.com",
            azure_content_understanding_key="test-key-12345",
        )
        with mock_patch("app.core.dependencies.get_settings", return_value=test_settings):
            service = get_content_understanding_service()
        assert isinstance(service, ContentUnderstandingServiceProtocol)
