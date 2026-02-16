# Configuration

All configuration is managed through environment variables. Both the backend and frontend use `.env` files for local development.

## Backend Configuration

The backend uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) to load configuration from environment variables with fallback to `.env`.

See [Environment Variables](../reference/environment-variables.md) for a full reference of all backend variables.

## Frontend Configuration

The frontend uses Next.js environment variables. Variables prefixed with `NEXT_PUBLIC_` are available in the browser.

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api/v1` |

## Azure Content Understanding

The backend requires credentials for the Azure Content Understanding service:

```env
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://<resource>.cognitiveservices.azure.com
AZURE_CONTENT_UNDERSTANDING_KEY=<your-key>
```

!!! warning
    Never commit real credentials. Use `.env` files which are gitignored.
