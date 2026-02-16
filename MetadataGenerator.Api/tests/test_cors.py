"""Tests for CORS middleware configuration."""

from fastapi.testclient import TestClient


class TestCorsMiddleware:
    """CORS middleware tests."""

    def test_cors_allows_configured_origin(self, client: TestClient) -> None:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_rejects_unknown_origin(self, client: TestClient) -> None:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://evil.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        # When the origin is not allowed, the header is absent
        assert "access-control-allow-origin" not in response.headers
