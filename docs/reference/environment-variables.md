# Environment Variables

All environment variables used by the Metadata Generator services.

## Backend (`MetadataGenerator.Api`)

Create a `.env` file in `MetadataGenerator.Api/` or export variables in your shell.

### Required

| Variable | Example | Description |
|----------|---------|-------------|
| `AZURE_CONTENT_UNDERSTANDING_ENDPOINT` | `https://my-resource.cognitiveservices.azure.com/` | Azure Content Understanding service endpoint |
| `AZURE_CONTENT_UNDERSTANDING_KEY` | `abc123...` | API key for Azure Content Understanding |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Metadata Generator API` | Application display name |
| `ENVIRONMENT` | `development` | Runtime environment identifier |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `API_V1_PREFIX` | `/api/v1` | API version prefix |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | JSON array of allowed CORS origins |

### Example `.env`

```env
APP_NAME=Metadata Generator API
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=["http://localhost:3000"]
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://my-resource.cognitiveservices.azure.com/
AZURE_CONTENT_UNDERSTANDING_KEY=your-api-key-here
```

## Frontend (`MetadataGenerator.Web`)

Create a `.env.local` file in `MetadataGenerator.Web/`.

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |

### Example `.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```
