# Configuration Reference

Complete reference for all configurable options in the Metadata Generator.

## Backend Configuration

The backend uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management. All settings can be provided via environment variables or a `.env` file.

### Application Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `APP_NAME` | `str` | `Metadata Generator API` | Application name used in logs and health endpoint |
| `ENVIRONMENT` | `str` | `development` | Runtime environment (`development`, `staging`, `production`) |
| `DEBUG` | `bool` | `false` | Enable debug mode (extra logging, detailed errors) |
| `LOG_LEVEL` | `str` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `API_V1_PREFIX` | `str` | `/api/v1` | URL prefix for versioned API endpoints |

### CORS Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ALLOWED_ORIGINS` | `list[str]` | `["http://localhost:3000"]` | Origins allowed for CORS requests |

### Azure Content Understanding

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `AZURE_CONTENT_UNDERSTANDING_ENDPOINT` | `str` | — | Azure Content Understanding service endpoint URL |
| `AZURE_CONTENT_UNDERSTANDING_KEY` | `str` | `""` (empty) | API key. Leave empty to use Entra ID (`DefaultAzureCredential`) |

### Webhook

| Setting | Type | Default | Description |
|---------|------|---------|------------|
| `WEBHOOK_API_KEYS` | `list[str]` | `[]` | Allowed API keys for webhook authentication |

## Frontend Configuration

The frontend uses Next.js environment variables. Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser. Server-only variables (no prefix) are used by the Route Handler proxy.

### Public Variables (browser)

| Variable | Default | Description |
|----------|---------|------------|
| `NEXT_PUBLIC_API_URL` | `/api/v1` | API base URL used in browser fetch calls |

### Server Variables (proxy)

| Variable | Default | Description |
|----------|---------|------------|
| `BACKEND_URL` | `http://localhost:8000` | Backend origin for the server-side Route Handler proxy |

## File Limits

These limits are enforced by the API:

| Limit | Value | Applies To |
|-------|-------|-----------|
| Max image file size | 10 MB | Image uploads |
| Max audio duration | 10 minutes | Audio uploads |
| Max batch size | 20 files | Batch uploads |
| Supported image formats | JPEG, PNG, TIFF, BMP, WebP | Image analysis |
| Supported audio formats | MP3, WAV, FLAC, OGG, M4A | Audio analysis |
