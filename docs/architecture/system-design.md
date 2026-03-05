# System Design

## Technology Stack

### Backend

| Layer | Technology | Version |
|-------|-----------|---------|
| Runtime | Python | 3.12+ |
| Framework | FastAPI | ≥ 0.115 |
| Server | Uvicorn | ≥ 0.34 |
| Configuration | Pydantic Settings | ≥ 2.7 |
| Package Manager | uv | Latest |
| Linting | Ruff | ≥ 0.9 |
| Type Checking | mypy (strict) | ≥ 1.14 |
| Testing | pytest + httpx | Latest |

### Frontend

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Next.js (App Router) | 16.x |
| UI Library | React | 19.x |
| Language | TypeScript (strict) | 5.x |
| Styling | Tailwind CSS | 4.x |
| Testing | Vitest + React Testing Library | Latest |
| Package Manager | pnpm | Latest |

### AI Service

| Service | Provider |
|---------|----------|
| Image & Audio Analysis | Azure Content Understanding |

## Project Layout

```
metadata-generator/
├── MetadataGenerator.Api/       # Backend API (FastAPI)
│   ├── app/
│   │   ├── core/                # Config (Pydantic Settings), dependencies (DI)
│   │   ├── middleware/          # Correlation ID middleware
│   │   ├── models/             # Pydantic request/response models
│   │   ├── routers/            # API endpoints (image, audio, batch, webhook, health)
│   │   ├── services/           # Azure Content Understanding service layer
│   │   └── utils/              # File validation, EXIF extraction, audio utils
│   └── tests/                  # pytest suite (137 tests, 88% coverage)
├── MetadataGenerator.Web/       # Frontend (Next.js)
│   └── src/
│       ├── app/                # Pages, layouts & API proxy route handler
│       │   └── api/v1/[...path]/ # Catch-all proxy to backend (600 s timeout, undici Agent)
│       ├── components/         # UI components (FileUpload, TileGrid, ImageTile, AudioTile, etc.)
│       ├── hooks/              # Custom React hooks
│       ├── lib/                # Typed API client, shared types, utilities
│       └── styles/             # Tailwind CSS theme tokens
├── docs/                        # MkDocs documentation (Material theme)
├── specs/                       # PRD, feature specs, tasks, ADRs
├── scripts/                     # Install scripts (bash, PowerShell)
└── mkdocs.yml                   # Documentation config
```

## Key Design Decisions

Architecture Decision Records (ADRs) are maintained in the `specs/adr/` directory at the repository root.

### Frontend Proxy Architecture

The frontend uses a **Next.js Route Handler** (`app/api/v1/[...path]/route.ts`) as a server-side proxy to the backend API instead of direct browser-to-backend calls. This design:

- **Eliminates CORS issues** in all deployment environments (local, dev containers, Codespaces)
- **Supports long-running requests** with a configurable 600-second timeout and a custom `undici` `Agent` that extends both `headersTimeout` and `bodyTimeout` to match
- **Simplifies deployment** — only one origin needs to be exposed to users

!!! note "Timeout History"
    The proxy timeout was originally 120 s but was increased to 600 s (10 min) after Azure audio analysis was found to exceed earlier limits. A custom `undici.Agent` is required because Node.js's built-in fetch has a default `headersTimeout` of 300 s that cannot be overridden via `AbortController` alone.

### Authentication Strategy

The backend uses `DefaultAzureCredential` from `azure-identity` for Azure service authentication. This provides a credential chain that works across environments:

- **Local development**: Azure CLI (`az login`)
- **CI/CD**: Environment variables (service principal)
- **Production**: Managed Identity (zero-secret deployment)
- **Fallback**: API key-based auth when `AZURE_CONTENT_UNDERSTANDING_KEY` is set

### Frontend Upload Strategy

The frontend uploads files **one at a time, sequentially** rather than in a single batch request. This avoids proxy timeout issues when batch requests contain audio files that take several minutes to analyse.

- **Images** use the synchronous `POST /api/v1/analyze/image` endpoint (~30 s each).
- **Audio files** use an **async submit + poll** pattern:
  1. `POST /api/v1/analyze/audio/submit` — returns a `job_id` immediately (HTTP 202).
  2. The frontend polls `GET /api/v1/analyze/audio/status/{job_id}` every 5 seconds until the status is `completed` or `failed`.
- Results are displayed progressively as each file completes.

The backend batch endpoint (`POST /api/v1/analyze/batch`) still exists for direct API consumers. It uses `asyncio.Semaphore` with a concurrency limit of 5 and processes files concurrently via `asyncio.gather()`.

### SDK Polling Interval

The Azure Content Understanding SDK polls `analyzerResults/{id}` every 30 seconds by default. The service overrides this to **5 seconds** via the `polling_interval` parameter on `begin_analyze_binary()` to detect completion faster.
