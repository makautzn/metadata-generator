"""Metadata Generator API — FastAPI application entry point.

This module creates and configures the FastAPI application including:
- Lifespan context manager for startup/shutdown events
- CORS middleware
- Correlation ID middleware
- API router mounting
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.dependencies import get_settings
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.routers import audio, batch, health, image, webhook

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — runs on startup and shutdown."""
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    logger.info("Starting %s (env=%s)", settings.app_name, settings.environment)
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Application factory — builds and returns a fully configured FastAPI app."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    # --- Middleware (order matters: last added = first executed) -----------
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Routers ----------------------------------------------------------
    app.include_router(health.router)
    app.include_router(image.router)
    app.include_router(audio.router)
    app.include_router(batch.router)
    app.include_router(webhook.router)

    return app


app = create_app()
