# Configuration

All configuration is managed through environment variables. Both the backend and frontend use `.env` files for local development.

## Backend Configuration

The backend uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) to load configuration from environment variables with fallback to `.env`.

See [Environment Variables](../reference/environment-variables.md) for a full reference of all backend variables.

## Frontend Configuration

The frontend uses Next.js environment variables. Variables prefixed with `NEXT_PUBLIC_` are available in the browser.

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | API base URL used by the browser | `/api/v1` |
| `BACKEND_URL` | Backend origin for the server-side proxy (not exposed to browser) | `http://localhost:8000` |

!!! note
    The frontend uses a **server-side Route Handler proxy** to forward `/api/v1/*` requests to the backend. The browser never calls the backend directly. `NEXT_PUBLIC_API_URL` defaults to `/api/v1` (relative), and `BACKEND_URL` configures where the proxy forwards requests.

## Azure Content Understanding

The backend authenticates to Azure Content Understanding using **Microsoft Entra ID** by default. Alternatively, an API key can be used.

### Option 1: Entra ID Authentication (recommended)

```bash
# Log in with Azure CLI
az login
```

```env
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://<resource>.services.ai.azure.com
# Leave the key empty or omit it entirely
AZURE_CONTENT_UNDERSTANDING_KEY=
```

The backend uses `DefaultAzureCredential` which tries these credential sources in order:

1. Environment variables (service principal)
2. Managed Identity (Azure-hosted environments)
3. Azure CLI (`az login`)

### Option 2: API Key Authentication

```env
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://<resource>.services.ai.azure.com
AZURE_CONTENT_UNDERSTANDING_KEY=<your-key>
```

!!! warning
    Never commit real credentials. Use `.env` files which are gitignored.
