"""Application configuration using Pydantic Settings.

All configuration is loaded from environment variables with sensible defaults.
Use a `.env` file for local development.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Metadata Generator API")
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    api_v1_prefix: str = Field(default="/api/v1")
    debug: bool = Field(default=False)

    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="List of allowed CORS origins",
    )

    # Azure Content Understanding
    azure_content_understanding_endpoint: str = Field(
        default="",
        description="Azure Content Understanding service endpoint",
    )
    azure_content_understanding_key: str = Field(
        default="",
        description="Azure Content Understanding service API key",
    )

    # Webhook
    webhook_api_keys: list[str] = Field(
        default_factory=list,
        description="Allowed API keys for webhook authentication",
    )


def get_settings() -> Settings:
    """Factory function to create and return a Settings instance.

    Used as a FastAPI dependency to allow overriding in tests.
    """
    return Settings()
