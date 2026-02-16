"""Unit tests for analysis Pydantic models."""

import pytest
from pydantic import ValidationError

from app.models.analysis import AnalysisError, AudioAnalysisResult, ImageAnalysisResult


class TestImageAnalysisResult:
    """Tests for ImageAnalysisResult model."""

    def test_valid_image_result(self) -> None:
        result = ImageAnalysisResult(
            description="Ein Foto eines Gebäudes",
            keywords=["Gebäude", "Architektur", "Stadt"],
            caption="Historisches Gebäude in der Innenstadt",
        )
        assert result.description == "Ein Foto eines Gebäudes"
        assert len(result.keywords) == 3
        assert result.caption == "Historisches Gebäude in der Innenstadt"

    def test_empty_description_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ImageAnalysisResult(
                description="",
                keywords=["a", "b", "c"],
                caption="caption",
            )

    def test_too_few_keywords_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ImageAnalysisResult(
                description="desc",
                keywords=[],
                caption="caption",
            )

    def test_too_many_keywords_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ImageAnalysisResult(
                description="desc",
                keywords=[f"kw{i}" for i in range(20)],
                caption="caption",
            )

    def test_all_fields_non_empty(self) -> None:
        result = ImageAnalysisResult(
            description="desc",
            keywords=["a", "b", "c"],
            caption="cap",
        )
        assert result.description
        assert result.caption
        assert all(k for k in result.keywords)

    def test_keywords_between_3_and_15(self) -> None:
        for count in (3, 10, 15):
            result = ImageAnalysisResult(
                description="desc",
                keywords=[f"kw{i}" for i in range(count)],
                caption="cap",
            )
            assert 3 <= len(result.keywords) <= 15


class TestAudioAnalysisResult:
    """Tests for AudioAnalysisResult model."""

    def test_valid_audio_result(self) -> None:
        result = AudioAnalysisResult(
            description="Ein Interview zum Thema Klimawandel",
            keywords=["Klima", "Interview", "Umwelt"],
            summary="Das Interview behandelt den Klimawandel",
        )
        assert result.description == "Ein Interview zum Thema Klimawandel"
        assert len(result.keywords) == 3
        assert result.summary == "Das Interview behandelt den Klimawandel"

    def test_empty_summary_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AudioAnalysisResult(
                description="desc",
                keywords=["a", "b", "c"],
                summary="",
            )

    def test_all_fields_non_empty(self) -> None:
        result = AudioAnalysisResult(
            description="desc",
            keywords=["a", "b", "c"],
            summary="summary",
        )
        assert result.description
        assert result.summary
        assert all(k for k in result.keywords)


class TestAnalysisError:
    """Tests for AnalysisError model."""

    def test_valid_error(self) -> None:
        err = AnalysisError(
            error_code="AZURE_HTTP_429",
            message="Rate limit exceeded",
        )
        assert err.error_code == "AZURE_HTTP_429"
        assert err.message == "Rate limit exceeded"

    def test_serialization_round_trip(self) -> None:
        err = AnalysisError(error_code="TEST", message="msg")
        data = err.model_dump()
        assert data == {"error_code": "TEST", "message": "msg"}
        err2 = AnalysisError.model_validate(data)
        assert err2 == err
