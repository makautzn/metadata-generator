"""FastAPI dependency providers.

Central location for all injectable dependencies used across the application.
"""

from functools import lru_cache

from app.core.config import Settings
from app.services.content_understanding import (
    AzureContentUnderstandingService,
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
    """
    settings = get_settings()
    return AzureContentUnderstandingService(
        endpoint=settings.azure_content_understanding_endpoint,
        key=settings.azure_content_understanding_key,
    )

