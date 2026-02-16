"""Health check router.

Provides /health and /health/ready endpoints for monitoring.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness check — confirms the service is running."""
    return {
        "status": "healthy",
        "service": "metadata-generator-api",
    }


@router.get("/health/ready")
async def readiness() -> dict[str, str]:
    """Readiness check — confirms the service is ready to accept traffic.

    Future iterations may check downstream dependencies (Azure, DB).
    """
    return {
        "status": "ready",
        "service": "metadata-generator-api",
    }
