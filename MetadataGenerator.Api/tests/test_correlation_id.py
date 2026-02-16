"""Tests for the correlation ID middleware."""

from fastapi.testclient import TestClient


class TestCorrelationIdMiddleware:
    """Correlation ID middleware tests."""

    def test_generates_correlation_id_when_absent(self, client: TestClient) -> None:
        response = client.get("/health")
        assert "x-correlation-id" in response.headers
        # Should be a valid UUID4 string (36 chars with hyphens)
        assert len(response.headers["x-correlation-id"]) == 36

    def test_forwards_existing_correlation_id(self, client: TestClient) -> None:
        custom_id = "my-custom-correlation-id"
        response = client.get(
            "/health",
            headers={"X-Correlation-ID": custom_id},
        )
        assert response.headers["x-correlation-id"] == custom_id
