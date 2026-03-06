"""Unit tests for the Speech-to-Text + LLM audio metadata service."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import AnalysisServiceError
from app.models.analysis import AudioAnalysisResult
from app.services.audio_speech_llm import SpeechAndLLMAudioService


def _build_service(
    endpoint: str = "https://test.services.ai.azure.com",
    model: str = "gpt-4o",
) -> SpeechAndLLMAudioService:
    mock_cred = AsyncMock()
    token = MagicMock()
    token.token = "test-token"
    mock_cred.get_token = AsyncMock(return_value=token)
    return SpeechAndLLMAudioService(
        endpoint=endpoint,
        credential=mock_cred,
        model=model,
    )


# ---------------------------------------------------------------------------
# Transcription tests
# ---------------------------------------------------------------------------


class TestTranscription:
    """Tests for the Speech-to-Text transcription step."""

    @pytest.mark.asyncio
    async def test_successful_transcription(self) -> None:
        service = _build_service()
        speech_response = {
            "combinedPhrases": [{"text": "Hallo, dies ist ein Test."}],
        }
        llm_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "Description": "Ein kurzer Testbeitrag.",
                                "Summary": "Kurzer Testbeitrag.",
                                "Keywords": ["Test", "Hallo", "Audio"],
                            }
                        )
                    }
                }
            ]
        }

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            # First call: speech, second call: LLM
            speech_resp = AsyncMock()
            speech_resp.status = 200
            speech_resp.json = AsyncMock(return_value=speech_response)

            llm_resp = AsyncMock()
            llm_resp.status = 200
            llm_resp.json = AsyncMock(return_value=llm_response)

            mock_session.post = MagicMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(side_effect=[speech_resp, llm_resp])
            mock_session.post.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await service.analyze_audio(b"fake-audio", "audio/mpeg")

        assert isinstance(result, AudioAnalysisResult)
        assert result.description == "Ein kurzer Testbeitrag."
        assert result.summary == "Kurzer Testbeitrag."
        assert "Test" in result.keywords

    @pytest.mark.asyncio
    async def test_speech_api_failure_raises(self) -> None:
        service = _build_service()

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = AsyncMock()
            resp.status = 400
            resp.text = AsyncMock(return_value="Bad request")

            mock_session.post = MagicMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(return_value=resp)
            mock_session.post.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(AnalysisServiceError) as exc_info:
                await service.analyze_audio(b"fake-audio", "audio/mpeg")
            assert "SPEECH_HTTP_400" in exc_info.value.error_code

    @pytest.mark.asyncio
    async def test_empty_transcript_raises(self) -> None:
        service = _build_service()

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            resp = AsyncMock()
            resp.status = 200
            resp.json = AsyncMock(return_value={"combinedPhrases": []})

            mock_session.post = MagicMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(return_value=resp)
            mock_session.post.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(AnalysisServiceError) as exc_info:
                await service.analyze_audio(b"fake-audio", "audio/mpeg")
            assert exc_info.value.error_code == "EMPTY_TRANSCRIPT"


# ---------------------------------------------------------------------------
# LLM metadata extraction tests
# ---------------------------------------------------------------------------


class TestMetadataExtraction:
    """Tests for the OpenAI chat completion metadata extraction step."""

    @pytest.mark.asyncio
    async def test_openai_failure_raises(self) -> None:
        service = _build_service()

        speech_response = {"combinedPhrases": [{"text": "Ein Test."}]}

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            speech_resp = AsyncMock()
            speech_resp.status = 200
            speech_resp.json = AsyncMock(return_value=speech_response)

            llm_resp = AsyncMock()
            llm_resp.status = 500
            llm_resp.text = AsyncMock(return_value="Internal error")

            mock_session.post = MagicMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(side_effect=[speech_resp, llm_resp])
            mock_session.post.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(AnalysisServiceError) as exc_info:
                await service.analyze_audio(b"fake-audio", "audio/mpeg")
            assert "OPENAI_HTTP_500" in exc_info.value.error_code


# ---------------------------------------------------------------------------
# LLM response parsing tests
# ---------------------------------------------------------------------------


class TestParseLLMResponse:
    """Tests for _parse_llm_response static method."""

    def test_valid_json(self) -> None:
        raw = json.dumps({
            "Description": "Eine Beschreibung.",
            "Summary": "Kurze Zusammenfassung.",
            "Keywords": ["Wort1", "Wort2", "Wort3"],
        })
        result = SpeechAndLLMAudioService._parse_llm_response(raw, "transcript text")
        assert result.description == "Eine Beschreibung."
        assert result.summary == "Kurze Zusammenfassung."
        assert result.keywords == ["Wort1", "Wort2", "Wort3"]

    def test_json_with_markdown_fences(self) -> None:
        raw = '```json\n{"Description": "Desc", "Summary": "Sum", "Keywords": ["A"]}\n```'
        result = SpeechAndLLMAudioService._parse_llm_response(raw, "transcript")
        assert result.description == "Desc"
        assert result.summary == "Sum"
        assert result.keywords == ["A"]

    def test_invalid_json_falls_back_to_transcript(self) -> None:
        result = SpeechAndLLMAudioService._parse_llm_response("not json at all", "my transcript")
        assert result.description == "my transcript"
        assert result.summary == "my transcript"
        assert "Audio" in result.keywords

    def test_empty_fields_use_transcript_fallback(self) -> None:
        raw = json.dumps({"Description": "", "Summary": "", "Keywords": []})
        result = SpeechAndLLMAudioService._parse_llm_response(raw, "fallback transcript")
        assert result.description == "fallback transcript"
        assert result.summary == "fallback transcript"
        assert len(result.keywords) >= 1

    def test_keywords_list_truncated_to_15(self) -> None:
        raw = json.dumps({
            "Description": "Desc",
            "Summary": "Sum",
            "Keywords": [f"kw{i}" for i in range(20)],
        })
        result = SpeechAndLLMAudioService._parse_llm_response(raw, "t")
        assert len(result.keywords) <= 15

    def test_keywords_non_list_uses_fallback(self) -> None:
        raw = json.dumps({
            "Description": "Desc",
            "Summary": "Sum",
            "Keywords": "not a list",
        })
        result = SpeechAndLLMAudioService._parse_llm_response(raw, "t")
        assert isinstance(result.keywords, list)
        assert len(result.keywords) >= 1


# ---------------------------------------------------------------------------
# Composite service tests
# ---------------------------------------------------------------------------


class TestCompositeService:
    """Tests for CompositeContentUnderstandingService routing."""

    @pytest.mark.asyncio
    async def test_image_routed_to_cu(self) -> None:
        from app.services.content_understanding import CompositeContentUnderstandingService

        cu = AsyncMock()
        cu.analyze_image = AsyncMock(return_value=MagicMock())
        audio = AsyncMock()

        composite = CompositeContentUnderstandingService(cu_service=cu, audio_service=audio)
        await composite.analyze_image(b"img", "image/jpeg")
        cu.analyze_image.assert_awaited_once_with(b"img", "image/jpeg")
        audio.analyze_audio.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_audio_routed_to_speech_llm(self) -> None:
        from app.services.content_understanding import CompositeContentUnderstandingService

        cu = AsyncMock()
        audio = AsyncMock()
        audio.analyze_audio = AsyncMock(
            return_value=AudioAnalysisResult(
                description="d", keywords=["k"], summary="s"
            )
        )

        composite = CompositeContentUnderstandingService(cu_service=cu, audio_service=audio)
        result = await composite.analyze_audio(b"aud", "audio/mpeg")
        audio.analyze_audio.assert_awaited_once_with(b"aud", "audio/mpeg")
        cu.analyze_audio.assert_not_awaited()
        assert result.description == "d"
