"""Audio metadata extraction via Azure Speech-to-Text + Azure OpenAI.

This service works around a known issue where Azure Content Understanding's
audio pipeline (``prebuilt-audio``) hangs indefinitely in a "Running" state.
It achieves the same result by:

1. Transcribing audio using the Azure Speech Fast Transcription API.
2. Sending the transcript to Azure OpenAI (``gpt-4o``) with a structured
   prompt to extract Description, Summary, and Keywords — identical fields
   to the CU ``audioMetadataExtractor`` analyzer.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import aiohttp
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity.aio import DefaultAzureCredential

from app.core.exceptions import AnalysisServiceError
from app.models.analysis import AudioAnalysisResult

logger = logging.getLogger(__name__)

# Maps MIME types to locale hints for Speech-to-Text
_DEFAULT_LOCALES = ["de-DE", "en-US"]

_METADATA_SYSTEM_PROMPT = """\
You are a metadata extraction assistant. Given a transcript of an audio file, \
extract structured metadata in German (Deutsch).

Return a JSON object with exactly these keys:
- "Description": A detailed description of the audio content in German.
- "Summary": A single, concise sentence in German summarising the audio content. \
Maximum 30 words. Must be exactly ONE sentence.
- "Keywords": A JSON array of 5 to 10 relevant German keywords describing the audio content.

Return ONLY valid JSON, no markdown fences, no commentary."""


class SpeechAndLLMAudioService:
    """Transcribe audio via Azure Speech, then extract metadata via Azure OpenAI.

    Requires the Azure AI Services resource to have:
    - Speech-to-Text enabled (for fast transcription)
    - An Azure OpenAI model accessible via the AI Foundry inference API
    """

    def __init__(
        self,
        endpoint: str,
        *,
        credential: AsyncTokenCredential | None = None,
        model: str = "gpt-4o",
        locales: list[str] | None = None,
    ) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._credential = credential or DefaultAzureCredential()
        self._owns_credential = credential is None
        self._model = model
        self._locales = locales or list(_DEFAULT_LOCALES)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def analyze_audio(self, file_bytes: bytes, content_type: str) -> AudioAnalysisResult:
        """Transcribe audio and extract metadata using LLM."""
        transcript = await self._transcribe(file_bytes, content_type)
        if not transcript.strip():
            raise AnalysisServiceError(
                error_code="EMPTY_TRANSCRIPT",
                message="Speech-to-Text returned an empty transcript for the audio file",
            )
        logger.info("Transcript length: %d chars", len(transcript))
        return await self._extract_metadata(transcript)

    # ------------------------------------------------------------------
    # Step 1: Speech-to-Text via Fast Transcription API
    # ------------------------------------------------------------------

    async def _transcribe(self, file_bytes: bytes, content_type: str) -> str:
        """Call Azure Speech Fast Transcription to get a combined transcript."""
        token = await self._credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        )
        url = (
            f"{self._endpoint}/speechtotext/transcriptions:transcribe"
            "?api-version=2024-11-15"
        )

        definition = json.dumps({
            "locales": self._locales,
            "profanityFilterMode": "None",
        })

        form = aiohttp.FormData()
        form.add_field(
            "audio",
            file_bytes,
            filename="audio",
            content_type=content_type,
        )
        form.add_field("definition", definition, content_type="application/json")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers={"Authorization": f"Bearer {token.token}"},
                data=form,
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.error("Speech transcription failed (%d): %s", resp.status, body[:500])
                    raise AnalysisServiceError(
                        error_code=f"SPEECH_HTTP_{resp.status}",
                        message=f"Speech-to-Text request failed: {body[:300]}",
                    )
                result = await resp.json()

        phrases = result.get("combinedPhrases", [])
        return " ".join(p.get("text", "") for p in phrases).strip()

    # ------------------------------------------------------------------
    # Step 2: Metadata extraction via Azure OpenAI chat completion
    # ------------------------------------------------------------------

    async def _extract_metadata(self, transcript: str) -> AudioAnalysisResult:
        """Send the transcript to Azure OpenAI for metadata extraction."""
        token = await self._credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        )
        url = (
            f"{self._endpoint}/models/chat/completions"
            "?api-version=2024-05-01-preview"
        )

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": _METADATA_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Transcript:\n\n{transcript}",
                },
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers={
                    "Authorization": f"Bearer {token.token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.error("OpenAI chat failed (%d): %s", resp.status, body[:500])
                    raise AnalysisServiceError(
                        error_code=f"OPENAI_HTTP_{resp.status}",
                        message=f"Azure OpenAI request failed: {body[:300]}",
                    )
                result = await resp.json()

        raw_content = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return self._parse_llm_response(raw_content, transcript)

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_llm_response(raw: str, transcript: str) -> AudioAnalysisResult:
        """Parse the LLM JSON response into an AudioAnalysisResult."""
        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first and last fence lines
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines).strip()

        try:
            data: dict[str, Any] = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse LLM JSON response: %s", exc)
            # Fallback: use transcript as description
            return AudioAnalysisResult(
                description=transcript[:500],
                keywords=["Audio", "Transkript", "Inhalt"],
                summary=transcript[:200],
            )

        description = data.get("Description", "") or transcript[:500]
        summary = data.get("Summary", "") or description[:200]
        keywords = data.get("Keywords", [])

        if not isinstance(keywords, list) or not keywords:
            keywords = ["Audio", "Transkript", "Inhalt"]
        else:
            keywords = [str(k) for k in keywords if k][:15]

        if not description:
            description = transcript[:500]
        if not summary:
            summary = description[:200]

        return AudioAnalysisResult(
            description=description,
            keywords=keywords,
            summary=summary,
        )
