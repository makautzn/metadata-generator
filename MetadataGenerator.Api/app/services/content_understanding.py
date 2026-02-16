"""Azure Content Understanding integration service.

Provides an async abstraction over the Azure Content Understanding SDK for
analysing image and audio files.  Includes retry logic with exponential
back-off for transient errors (HTTP 429 / 503).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol, runtime_checkable

from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalyzeResult, ContentField
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceRequestError

from app.core.exceptions import (
    AnalysisServiceError,
    ConfigurationError,
    TransientError,
)
from app.models.analysis import AudioAnalysisResult, ImageAnalysisResult

logger = logging.getLogger(__name__)

# Azure Content Understanding custom analyser identifiers
PREBUILT_IMAGE_ANALYZER: str = "imageMetadataExtractor"
PREBUILT_AUDIO_ANALYZER: str = "audioMetadataExtractor"

# Transient HTTP status codes eligible for retry
_TRANSIENT_STATUS_CODES: frozenset[int] = frozenset({429, 503})


@runtime_checkable
class ContentUnderstandingServiceProtocol(Protocol):
    """Interface contract for content understanding services."""

    async def analyze_image(self, file_bytes: bytes, content_type: str) -> ImageAnalysisResult: ...

    async def analyze_audio(self, file_bytes: bytes, content_type: str) -> AudioAnalysisResult: ...


class AzureContentUnderstandingService:
    """Concrete implementation using the Azure Content Understanding SDK.

    Creates a fresh ``ContentUnderstandingClient`` per request to avoid
    connection-sharing issues in concurrent workloads.  Retry logic wraps
    the whole analyse-and-poll cycle.
    """

    def __init__(
        self,
        endpoint: str,
        key: str,
        *,
        max_retries: int = 3,
    ) -> None:
        if not endpoint or not key:
            raise ConfigurationError(
                error_code="MISSING_CONFIG",
                message="Azure Content Understanding endpoint and key are required",
            )
        self._endpoint = endpoint
        self._credential = AzureKeyCredential(key)
        self._max_retries = max_retries

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def analyze_image(self, file_bytes: bytes, content_type: str) -> ImageAnalysisResult:
        """Analyse an image and return structured metadata in German."""
        result = await self._analyze_with_retry(file_bytes, content_type, PREBUILT_IMAGE_ANALYZER)
        return self._parse_image_result(result)

    async def analyze_audio(self, file_bytes: bytes, content_type: str) -> AudioAnalysisResult:
        """Analyse an audio file and return structured metadata in German."""
        result = await self._analyze_with_retry(file_bytes, content_type, PREBUILT_AUDIO_ANALYZER)
        return self._parse_audio_result(result)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_client(self) -> ContentUnderstandingClient:
        """Instantiate a new SDK client (used as async context-manager)."""
        return ContentUnderstandingClient(
            endpoint=self._endpoint,
            credential=self._credential,
        )

    async def _analyze_with_retry(
        self,
        file_bytes: bytes,
        content_type: str,
        analyzer_id: str,
    ) -> AnalyzeResult:
        """Submit binary content for analysis with exponential-backoff retry."""
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                async with self._create_client() as client:
                    poller = await client.begin_analyze_binary(
                        analyzer_id=analyzer_id,
                        binary_input=file_bytes,
                        content_type=content_type,
                    )
                    result: AnalyzeResult = await poller.result()
                    logger.info(
                        "Analysis complete (analyzer=%s, attempt=%d)",
                        analyzer_id,
                        attempt + 1,
                    )
                    return result

            except HttpResponseError as exc:
                status = exc.status_code or 0
                is_transient = status in _TRANSIENT_STATUS_CODES

                if is_transient and attempt < self._max_retries:
                    wait = 2**attempt
                    logger.warning(
                        "Transient error HTTP %d on attempt %d/%d — retrying in %ds",
                        status,
                        attempt + 1,
                        self._max_retries,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    last_error = exc
                    continue

                if is_transient:
                    # All retry attempts exhausted for a transient error
                    raise TransientError(
                        error_code="MAX_RETRIES_EXCEEDED",
                        message=f"Failed after {self._max_retries} retries",
                    ) from exc

                logger.error(
                    "Non-retryable Azure error HTTP %d: %s",
                    status,
                    exc.message,
                )
                raise AnalysisServiceError(
                    error_code=f"AZURE_HTTP_{status}",
                    message=str(exc),
                ) from exc

            except ServiceRequestError as exc:
                logger.error("Azure service request error: %s", exc)
                raise AnalysisServiceError(
                    error_code="SERVICE_REQUEST_ERROR",
                    message=str(exc),
                ) from exc

        # Exhausted all retry attempts
        raise TransientError(
            error_code="MAX_RETRIES_EXCEEDED",
            message=f"Failed after {self._max_retries} retries",
        ) from last_error

    # ------------------------------------------------------------------
    # Result parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_field(fields: dict[str, ContentField] | None, name: str) -> str:
        """Safely extract a string value from an Azure ContentField dict."""
        if not fields:
            return ""
        field = fields.get(name)
        if field is None:
            return ""
        value: Any = getattr(field, "value", None)
        return str(value) if value is not None else ""

    @staticmethod
    def _truncate_to_first_sentence(text: str) -> str:
        """Return only the first sentence of *text*.

        Splits on common sentence-ending punctuation (. ! ?) followed by
        whitespace or end-of-string and keeps only the first segment.
        """
        if not text:
            return text
        import re

        match = re.search(r"[.!?](?:\s|$)", text)
        if match:
            return text[: match.end()].strip()
        return text

    @staticmethod
    def _extract_keywords(fields: dict[str, ContentField] | None, markdown: str) -> list[str]:
        """Extract keywords from fields or derive from markdown content.

        The prebuilt analysers may provide a ``Keywords`` field.  If absent,
        fall back to extracting salient words from the markdown summary.
        """
        if fields:
            kw_field = fields.get("Keywords")
            if kw_field is not None:
                value: Any = getattr(kw_field, "value", None)
                if isinstance(value, list):
                    return [
                        str(getattr(k, "value", k))
                        for k in value
                        if k
                    ]
                if isinstance(value, str) and value:
                    return [k.strip() for k in value.split(",") if k.strip()]

        # Fallback: extract unique non-trivial words from markdown
        if markdown:
            words = markdown.split()
            seen: set[str] = set()
            keywords: list[str] = []
            for word in words:
                cleaned = word.strip(".,;:!?\"'()[]{}#*-_")
                # Skip markdown artefacts (links, references, short tokens)
                if (
                    len(cleaned) > 3
                    and cleaned.lower() not in seen
                    and not any(ch in cleaned for ch in "[]()#|/")
                ):
                    seen.add(cleaned.lower())
                    keywords.append(cleaned)
                if len(keywords) >= 10:
                    break
            if keywords:
                return keywords

        return ["Allgemein", "Inhalt", "Medium"]

    def _parse_image_result(self, result: AnalyzeResult) -> ImageAnalysisResult:
        """Map an ``AnalyzeResult`` to our ``ImageAnalysisResult`` model."""
        contents = result.contents
        if not contents:
            raise AnalysisServiceError(
                error_code="EMPTY_RESULT",
                message="Azure returned an empty analysis result for the image",
            )

        content = contents[0]
        fields = content.fields
        markdown = content.markdown or ""

        description = self._extract_field(fields, "Description") or markdown[:500]
        caption = self._extract_field(fields, "Caption") or description[:200]
        keywords = self._extract_keywords(fields, markdown)

        return ImageAnalysisResult(
            description=description,
            keywords=keywords,
            caption=caption,
        )

    def _parse_audio_result(self, result: AnalyzeResult) -> AudioAnalysisResult:
        """Map an ``AnalyzeResult`` to our ``AudioAnalysisResult`` model."""
        contents = result.contents
        if not contents:
            raise AnalysisServiceError(
                error_code="EMPTY_RESULT",
                message="Azure returned an empty analysis result for the audio",
            )

        content = contents[0]
        fields = content.fields
        markdown = content.markdown or ""

        description = self._extract_field(fields, "Description") or markdown[:500]
        raw_summary = self._extract_field(fields, "Summary") or description[:200]
        summary = self._truncate_to_first_sentence(raw_summary)
        keywords = self._extract_keywords(fields, markdown)

        return AudioAnalysisResult(
            description=description,
            keywords=keywords,
            summary=summary,
        )
