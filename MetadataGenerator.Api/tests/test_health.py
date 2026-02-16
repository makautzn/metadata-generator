"""Tests for health check endpoints."""

from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Health endpoint tests."""

    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_body(self, client: TestClient) -> None:
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["service"] == "metadata-generator-api"

    def test_readiness_returns_200(self, client: TestClient) -> None:
        response = client.get("/health/ready")
        assert response.status_code == 200

    def test_readiness_body(self, client: TestClient) -> None:
        data = client.get("/health/ready").json()
        assert data["status"] == "ready"
        assert data["service"] == "metadata-generator-api"
