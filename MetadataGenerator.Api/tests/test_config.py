"""Tests for application configuration."""

from app.core.config import Settings


class TestSettings:
    """Settings configuration tests."""

    def test_default_app_name(self) -> None:
        settings = Settings(
            azure_content_understanding_endpoint="",
            azure_content_understanding_key="",
        )
        assert settings.app_name == "Metadata Generator API"

    def test_default_environment(self) -> None:
        settings = Settings()
        assert settings.environment == "development"

    def test_default_api_prefix(self) -> None:
        settings = Settings()
        assert settings.api_v1_prefix == "/api/v1"

    def test_custom_values(self) -> None:
        settings = Settings(
            app_name="Custom",
            environment="production",
            log_level="WARNING",
            debug=True,
        )
        assert settings.app_name == "Custom"
        assert settings.environment == "production"
        assert settings.log_level == "WARNING"
        assert settings.debug is True

    def test_default_allowed_origins(self) -> None:
        settings = Settings()
        assert "http://localhost:3000" in settings.allowed_origins
