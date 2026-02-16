"""Shared test fixtures for the Metadata Generator API test suite."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.dependencies import get_settings
from app.main import create_app


def _test_settings() -> Settings:
    """Return a Settings instance configured for testing."""
    return Settings(
        app_name="Test Metadata Generator API",
        environment="testing",
        log_level="DEBUG",
        debug=True,
        allowed_origins=["http://localhost:3000", "http://testserver"],
        azure_content_understanding_endpoint="https://test.cognitiveservices.azure.com",
        azure_content_understanding_key="test-key",
    )


@pytest.fixture()
def settings() -> Settings:
    """Provide test settings."""
    return _test_settings()


@pytest.fixture()
def client() -> TestClient:
    """Provide a TestClient with overridden settings."""
    app = create_app()
    app.dependency_overrides[get_settings] = _test_settings
    return TestClient(app)
