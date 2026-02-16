# Development Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- pnpm (install via `npm install -g pnpm`)
- uv (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Daily Workflow

### Backend (MetadataGenerator.Api)

```bash
cd MetadataGenerator.Api

# Sync dependencies
make sync

# Start dev server with hot-reload
make dev

# Run linter
make lint

# Auto-fix lint and format
make fmt

# Run type-checker
make typecheck

# Run tests
make test

# Run tests with coverage
make test-cov
```

### Frontend (MetadataGenerator.Web)

```bash
cd MetadataGenerator.Web

# Install dependencies
pnpm install

# Start dev server
pnpm dev

# Lint & format check
pnpm lint

# Auto-fix lint & format
pnpm lint:fix

# Type-check
pnpm typecheck

# Run tests
pnpm test
```

### Documentation

```bash
# Serve docs locally
source .venv/bin/activate
mkdocs serve

# Build docs (strict mode)
mkdocs build --strict
```

## Code Standards

- **Backend**: Follow Ruff rules (E, W, F, I, N, UP, B, S, T20, RUF). mypy strict mode.
- **Frontend**: ESLint + Prettier. TypeScript strict mode.
- **Coverage**: Minimum 85% for both backend and frontend.
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/).

## Project Structure

See [System Design](../architecture/system-design.md) for the full project layout.
