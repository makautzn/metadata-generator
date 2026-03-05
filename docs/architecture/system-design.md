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
│   └── tests/                  # pytest suite (137 tests)
├── MetadataGenerator.Web/       # Frontend (Next.js)
│   └── src/
│       ├── app/                # Pages, layouts & API proxy route handler
│       │   └── api/v1/[...path]/ # Catch-all proxy to backend (120 s timeout)
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
- **Supports long-running requests** with a configurable 120-second timeout (Azure analysis can take 30+ seconds)
- **Simplifies deployment** — only one origin needs to be exposed to users

### Authentication Strategy

The backend uses `DefaultAzureCredential` from `azure-identity` for Azure service authentication. This provides a credential chain that works across environments:

- **Local development**: Azure CLI (`az login`)
- **CI/CD**: Environment variables (service principal)
- **Production**: Managed Identity (zero-secret deployment)
- **Fallback**: API key-based auth when `AZURE_CONTENT_UNDERSTANDING_KEY` is set

### Concurrency Model

Batch analysis uses `asyncio.Semaphore` with a concurrency limit of 5 to prevent overwhelming the Azure service. Files within a batch are processed concurrently via `asyncio.gather()`.
