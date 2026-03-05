# Environment Variables

All environment variables used by the Metadata Generator services.

## Backend (`MetadataGenerator.Api`)

Create a `.env` file in `MetadataGenerator.Api/` or export variables in your shell.

### Required

| Variable | Example | Description |
|----------|---------|-------------|
| `AZURE_CONTENT_UNDERSTANDING_ENDPOINT` | `https://my-resource.services.ai.azure.com` | Azure Content Understanding service endpoint |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_CONTENT_UNDERSTANDING_KEY` | _(empty)_ | API key for Azure Content Understanding. Leave empty to use Entra ID (`DefaultAzureCredential`) |
| `APP_NAME` | `Metadata Generator API` | Application display name |
| `ENVIRONMENT` | `development` | Runtime environment identifier |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `API_V1_PREFIX` | `/api/v1` | API version prefix |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | JSON array of allowed CORS origins |
| `WEBHOOK_API_KEYS` | `[]` | JSON array of API keys for webhook authentication |

### Example `.env` (Entra ID auth)

```env
APP_NAME=Metadata Generator API
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=["http://localhost:3000"]
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://my-resource.services.ai.azure.com
AZURE_CONTENT_UNDERSTANDING_KEY=
```

### Example `.env` (API key auth)

```env
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://my-resource.services.ai.azure.com
AZURE_CONTENT_UNDERSTANDING_KEY=your-api-key-here
```

## Frontend (`MetadataGenerator.Web`)

Create a `.env.local` file in `MetadataGenerator.Web/`.

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `/api/v1` | API base URL used in the browser (relative path routes through the proxy) |
| `BACKEND_URL` | `http://localhost:8000` | Backend origin used by the server-side Route Handler proxy (not exposed to browser) |

### Example `.env.local`

```env
# Usually no frontend env vars are needed for local development.
# The defaults work out of the box:
#   NEXT_PUBLIC_API_URL=/api/v1
#   BACKEND_URL=http://localhost:8000
```
