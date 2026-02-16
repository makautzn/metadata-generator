# 001 — Backend API Project Scaffolding

## Description

Set up the Python FastAPI backend project following the canonical stack and project layout defined in the engineering standards. This includes project initialization with `uv`, FastAPI application structure, configuration management, CORS middleware, health endpoints, and dev tooling (linting, type checking, testing framework).

## Dependencies

- None (first task)

## Technical Requirements

### Project Structure

```
MetadataGenerator.Api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization, lifespan, middleware
│   ├── routers/                # API route modules (empty initially)
│   │   └── __init__.py
│   ├── models/                 # Pydantic models (empty initially)
│   │   └── __init__.py
│   ├── services/               # Business logic layer (empty initially)
│   │   └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic Settings (env vars, Azure config)
│   │   └── dependencies.py     # FastAPI dependencies
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── conftest.py             # Shared pytest fixtures
├── pyproject.toml
├── .env.example
└── README.md
```

### Configuration

- Use Pydantic Settings (`BaseSettings`) for all configuration with `.env` file support
- Define settings for: Azure Content Understanding endpoint/key, allowed origins (CORS), application name, environment, log level
- Provide `.env.example` with all required variables (no real secrets)

### Application Setup (main.py)

- Use `@asynccontextmanager` lifespan for startup/shutdown hooks
- Configure CORS middleware allowing the frontend origin
- Mount `/api/v1/` prefix for all API routers
- Expose `/health` and `/health/ready` endpoints returning JSON status

### Dev Tooling

- Initialize project with `uv init` and Python 3.11+
- Add dev dependencies: `pytest`, `pytest-asyncio`, `httpx`, `ruff`, `mypy`
- Add production dependencies: `fastapi`, `uvicorn`, `pydantic-settings`, `python-dotenv`
- Configure `pyproject.toml` with Ruff rules, mypy strict mode, pytest settings
- Provide a `Makefile` or scripts for common dev commands (`lint`, `typecheck`, `test`, `dev`)

### Observability

- Configure structured JSON logging
- Include request correlation ID middleware
- Health endpoint must report service name and status

## Acceptance Criteria

- [x] `uv sync` installs all dependencies without errors
- [x] `uv run uvicorn app.main:app --reload` starts the server successfully
- [x] `GET /health` returns `200` with `{"status": "healthy", "service": "metadata-generator-api"}`
- [x] `GET /health/ready` returns `200`
- [x] CORS headers are present for configured origins
- [x] `uv run ruff check .` passes with no errors
- [x] `uv run mypy app` passes with no errors
- [x] `uv run pytest` runs and all scaffold tests pass
- [x] `.env.example` documents all required environment variables
- [x] OpenAPI docs are accessible at `/docs`

## Testing Requirements

- Unit test: health endpoint returns expected JSON structure and 200 status
- Unit test: readiness endpoint returns 200
- Unit test: CORS middleware allows configured origin
- Unit test: configuration loads from environment variables with defaults
- Integration test: application starts without errors using test configuration
- Coverage: ≥ 85% for scaffolding code
