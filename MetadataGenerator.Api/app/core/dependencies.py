"""FastAPI dependency providers.

Central location for all injectable dependencies used across the application.
"""

from functools import lru_cache

from app.core.config import Settings
from app.services.audio_speech_llm import SpeechAndLLMAudioService
from app.services.content_understanding import (
    AzureContentUnderstandingService,
    CompositeContentUnderstandingService,
    ContentUnderstandingServiceProtocol,
)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Uses lru_cache so environment variables are read once and reused.
    Override this dependency in tests to inject test configuration.
    """
    return Settings()


@lru_cache
def get_content_understanding_service() -> ContentUnderstandingServiceProtocol:
    """Create and return a Content Understanding service instance.

    Cached so that a single ``DefaultAzureCredential`` (and its internal
    HTTP session) is reused across requests instead of being recreated each
    time.  Override this dependency in tests to inject a mock service.

    Uses a composite service that routes images through Azure CU and audio
    through a direct Speech-to-Text + Azure OpenAI pipeline (workaround
    for CU audio pipeline stuck in "Running" state).
    """
    settings = get_settings()
    cu_service = AzureContentUnderstandingService(
        endpoint=settings.azure_content_understanding_endpoint,
        key=settings.azure_content_understanding_key,
    )
    audio_service = SpeechAndLLMAudioService(
        endpoint=settings.azure_content_understanding_endpoint,
        model=settings.azure_openai_model,
    )
    return CompositeContentUnderstandingService(
        cu_service=cu_service,
        audio_service=audio_service,
    )

