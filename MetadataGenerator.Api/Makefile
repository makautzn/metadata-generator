.PHONY: dev lint typecheck test test-cov fmt sync

# Install / sync dependencies
sync:
	uv sync

# Start dev server with hot-reload
dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Lint with Ruff
lint:
	uv run ruff check .

# Auto-fix lint issues
fmt:
	uv run ruff check --fix .
	uv run ruff format .

# Type-check with mypy
typecheck:
	uv run mypy app

# Run tests
test:
	uv run pytest

# Run tests with coverage report
test-cov:
	uv run pytest --cov=app --cov-report=term-missing --cov-report=html
