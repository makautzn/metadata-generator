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
│   │   ├── core/                # Config, dependencies
│   │   ├── middleware/          # Correlation ID, etc.
│   │   ├── models/             # Pydantic models
│   │   ├── routers/            # API endpoints
│   │   ├── services/           # Business logic
│   │   └── utils/              # Utilities
│   └── tests/                  # pytest suite
├── MetadataGenerator.Web/       # Frontend (Next.js)
│   └── src/
│       ├── app/                # Pages & layouts
│       ├── components/         # Shared components
│       ├── hooks/              # Custom hooks
│       ├── lib/                # API client, types, utils
│       └── styles/             # Theme tokens
├── docs/                        # MkDocs documentation
├── specs/                       # PRD, FRDs, tasks, ADRs
└── mkdocs.yml                   # Documentation config
```

## Key Design Decisions

Architecture Decision Records (ADRs) are maintained in the `specs/adr/` directory at the repository root.
