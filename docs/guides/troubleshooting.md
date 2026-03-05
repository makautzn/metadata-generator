# Troubleshooting

Common issues and solutions when developing or running the Metadata Generator.

## Backend Issues

### `ModuleNotFoundError: No module named 'app'`

Run the server from the `MetadataGenerator.Api` directory:

```bash
cd MetadataGenerator.Api
uv run uvicorn app.main:app --reload
```

### `429 Request Rate Too Large` from Azure

The Azure Content Understanding API is throttling requests. The SDK implements automatic retry with exponential back-off. If the issue persists:

- Reduce batch sizes
- Increase your Azure resource tier
- Check the `Retry-After` header value

### Tests fail with import errors

Ensure dev dependencies are installed:

```bash
cd MetadataGenerator.Api
uv sync
```

### CORS errors in browser console

In normal operation, the frontend uses a server-side proxy so CORS shouldn't be an issue. If you bypass the proxy and call the backend directly, check that `ALLOWED_ORIGINS` in your `.env` includes the frontend URL:

```env
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## Frontend Issues

### `pnpm install` fails

Ensure you have the correct Node.js version (≥ 20) and pnpm (≥ 10):

```bash
node --version
pnpm --version
```

### TypeScript errors after pulling changes

Run a fresh install and typecheck:

```bash
cd MetadataGenerator.Web
pnpm install
pnpm typecheck
```

### API requests fail in development ("Failed to fetch" or 502)

The frontend proxies all `/api/v1/*` requests through a Next.js Route Handler to the backend. Check:

1. **Backend is running** on port 8000:
   ```bash
   curl http://localhost:8000/health
   ```
2. **Proxy is working** through the frontend:
   ```bash
   curl http://localhost:3000/api/v1/analyze/batch -X POST
   ```
3. If using a custom backend URL, set `BACKEND_URL` in the frontend environment:
   ```env
   BACKEND_URL=http://localhost:8000
   ```

### "Internal Server Error" on file upload (long-running requests)

Azure Content Understanding analysis can take 30+ seconds for large files. The Route Handler proxy has a 120-second timeout. If you still see timeouts:

- Check the backend terminal for `Analysis complete` logs
- Ensure the backend isn't restarting mid-request (uvicorn `--reload` can cause this)
- Test the backend directly: `curl -X POST http://localhost:8000/api/v1/analyze/batch -F 'files=@photo.jpg'`

## Documentation Issues

### `mkdocs serve` fails

Activate the virtual environment first:

```bash
source .venv/bin/activate
mkdocs serve
```

If the virtual environment doesn't exist:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install mkdocs-material mkdocs-minify-plugin
```

## Azure Content Understanding

### `403 AuthenticationTypeDisabled: Key based authentication is disabled`

The Azure resource has API key authentication disabled. Switch to Entra ID authentication:

1. Clear the API key in `.env`:
   ```env
   AZURE_CONTENT_UNDERSTANDING_KEY=
   ```
2. Log in with Azure CLI:
   ```bash
   az login
   ```
3. Restart the backend server.

### `401 Unauthorized`

If using **Entra ID** (`DefaultAzureCredential`):

- Ensure you're logged in: `az account show`
- Verify your account has the correct RBAC role on the Azure AI resource
- Check the backend logs for which credential was used (look for `DefaultAzureCredential acquired a token from ...`)

If using **API key** auth:

- Verify `AZURE_CONTENT_UNDERSTANDING_KEY` is correct and not expired
- Ensure the key matches the endpoint's resource

### Timeout errors

Azure Content Understanding analysis can take 10–30+ seconds per file depending on size. The backend retries transient errors (HTTP 429, 503) with exponential back-off up to 3 times. The frontend proxy has a 120-second timeout for each request.

## Getting Help

If your issue isn't listed here:

1. Check the [GitHub Issues](https://github.com/makautzn/metadata-generator/issues)
2. Review the API logs for correlation IDs (they appear in the `X-Correlation-ID` response header)
3. Open a new issue with reproduction steps and correlation ID
