# Metadata Generator API

Backend API service for the Metadata Generator PoC, built with **FastAPI** and managed with **uv**.

## Quick Start

```bash
# Install dependencies
make sync

# Copy and edit environment variables
cp .env.example .env

# Start dev server (http://localhost:8000)
make dev
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make sync` | Install / sync dependencies |
| `make dev` | Start dev server with hot-reload |
| `make lint` | Lint with Ruff |
| `make fmt` | Auto-fix lint issues & format |
| `make typecheck` | Type-check with mypy |
| `make test` | Run tests |
| `make test-cov` | Run tests with coverage report |

## Project Structure

```
app/
├── core/          # Configuration, dependencies
├── middleware/     # Correlation ID, etc.
├── models/        # Pydantic request/response models
├── routers/       # FastAPI route handlers
├── services/      # Business logic & external integrations
└── utils/         # Shared utilities
tests/             # pytest test suite
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |
| `GET` | `/health/ready` | Readiness check |
| `GET` | `/api/v1/docs` | Swagger UI |
| `GET` | `/api/v1/redoc` | ReDoc |
