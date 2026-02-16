# Metadata Generator

AI-powered metadata extraction for images and audio files, built for editorial workflows. Upload media files and receive structured German-language metadata — descriptions, keywords, captions, and summaries — powered by [Azure AI Content Understanding](https://learn.microsoft.com/azure/ai-services/content-understanding/).

## Overview

The Metadata Generator is a full-stack PoC application designed for editorial teams (inspired by *DIE RHEINPFALZ*) to automate the tagging and description of media assets. It consists of:

- **Backend API** (`MetadataGenerator.Api`) — Python/FastAPI service that processes uploads via Azure AI Content Understanding
- **Frontend** (`MetadataGenerator.Web`) — Next.js/React web app with a clean, light editorial UI

### Features

| Capability | Details |
|---|---|
| **Image analysis** | Description, caption, keywords, and EXIF extraction for JPEG, PNG, TIFF, WebP (max 10 MB) |
| **Audio analysis** | Description, one-sentence summary, and keywords for MP3, WAV, OGG, FLAC, M4A, AAC, WMA (max 100 MB, max 15 min) |
| **Batch processing** | Upload multiple files at once with real-time progress tracking |
| **Copy & export** | One-click copy of metadata fields; export results as JSON or CSV |
| **Webhook integration** | Receive processing results via authenticated webhook callbacks |
| **German output** | All AI-generated metadata is in German |

### API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/health/ready` | Readiness probe (verifies Azure connectivity) |
| `POST` | `/api/v1/analyze/image` | Analyze a single image |
| `POST` | `/api/v1/analyze/audio` | Analyze a single audio file |
| `POST` | `/api/v1/analyze/batch` | Analyze multiple files in one request |
| `POST` | `/api/v1/webhook/results` | Receive webhook result callbacks |

Interactive API docs are available at `/api/v1/docs` (Swagger) and `/api/v1/redoc` when the backend is running.

---

## Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) (for Dev Container) **or** local installs of:
  - Python 3.12+
  - [uv](https://docs.astral.sh/uv/) (Python package manager)
  - Node.js 20+ with [pnpm](https://pnpm.io/)
- An **Azure AI Content Understanding** resource (endpoint URL + API key)

### 1. Clone and open

```bash
git clone https://github.com/makautzn/metadata-generator.git
cd metadata-generator
```

If using VS Code with Dev Containers, reopen in the container — all tooling is pre-installed.

### 2. Configure the backend

Create a `.env` file in `MetadataGenerator.Api/`:

```env
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://<your-resource>.services.ai.azure.com
AZURE_CONTENT_UNDERSTANDING_KEY=<your-api-key>
```

### 3. Start the backend

```bash
cd MetadataGenerator.Api
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify it's running:

```bash
curl http://localhost:8000/health
# → {"status":"healthy"}
```

### 4. Start the frontend

In a new terminal:

```bash
cd MetadataGenerator.Web
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 5. Upload a file

Drag and drop an image or audio file onto the upload area. Metadata results appear as tiles once processing completes.

---

## Project Structure

```
metadata-generator/
├── MetadataGenerator.Api/          # Python backend
│   ├── app/
│   │   ├── core/                   # Config, dependencies
│   │   ├── middleware/             # Correlation ID middleware
│   │   ├── models/                 # Pydantic request/response models
│   │   ├── routers/               # FastAPI route handlers
│   │   ├── services/              # Azure Content Understanding client
│   │   └── utils/                 # File validation, EXIF, audio utils
│   └── tests/                     # pytest test suite (118 tests, ~92% coverage)
├── MetadataGenerator.Web/          # Next.js frontend
│   └── src/
│       ├── app/                   # Page layout and entry point
│       ├── components/            # UI components (tiles, upload, progress)
│       ├── hooks/                 # React hooks (useFileUpload)
│       ├── lib/                   # API client, types
│       └── styles/                # Design tokens and theme
├── specs/                         # Product specs, feature docs, task definitions
│   ├── features/                  # Feature requirement documents
│   ├── tasks/                     # Implementation task specs
│   └── adr/                       # Architecture Decision Records
└── docs/                          # MkDocs documentation site
```

---

## Development

### Running Tests

**Backend:**

```bash
cd MetadataGenerator.Api
uv run python -m pytest tests/ -q          # run all tests
uv run python -m pytest tests/ --cov=app   # with coverage report
```

**Frontend:**

```bash
cd MetadataGenerator.Web
pnpm test              # run all tests
pnpm test:coverage     # with coverage
```

### Linting & Type Checking

**Backend:**

```bash
cd MetadataGenerator.Api
uv run ruff check app/ tests/     # lint
uv run mypy app/                  # type check
```

**Frontend:**

```bash
cd MetadataGenerator.Web
pnpm lint          # ESLint + Prettier
pnpm typecheck     # TypeScript
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, Pydantic, uvicorn |
| AI Service | Azure AI Content Understanding (`azure-ai-contentunderstanding`) |
| Frontend | Next.js 16, React 19, Tailwind CSS 4 |
| Testing | pytest + pytest-cov (backend), Vitest + Testing Library (frontend) |
| Tooling | uv, pnpm, Ruff, mypy, ESLint, Prettier |
| Dev Environment | Dev Containers, Docker |

---

## Configuration

All backend configuration is via environment variables (loaded from `.env`):

| Variable | Required | Description |
|---|---|---|
| `AZURE_CONTENT_UNDERSTANDING_ENDPOINT` | Yes | Azure AI Content Understanding endpoint URL |
| `AZURE_CONTENT_UNDERSTANDING_KEY` | Yes | Azure AI Content Understanding API key |
| `ALLOWED_ORIGINS` | No | CORS origins (default: `["http://localhost:3000"]`) |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |
| `ENVIRONMENT` | No | Environment name (default: `development`) |
| `WEBHOOK_API_KEYS` | No | Comma-separated API keys for webhook auth |

---

## License

See [LICENSE.md](LICENSE.md).
