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

### "Internal Server Error" or 502/504 on file upload

The frontend proxies requests through a Next.js Route Handler with a 600-second timeout and a custom `undici` `Agent`. Common causes and fixes:

**502 Bad Gateway (`UND_ERR_HEADERS_TIMEOUT`)**

Node.js's built-in `fetch` (undici) has a default `headersTimeout` of 300 s. If the backend takes longer, the proxy fails with a 502 before the `AbortController` timeout fires. The Route Handler uses a custom `undici.Agent` with `headersTimeout: 600_000` and `bodyTimeout: 600_000` to prevent this. If you see this error after modifying `route.ts`, ensure the `dispatcher` option is still in place.

**504 Gateway Timeout (audio files)**

Audio analysis can take 10–20+ minutes on Azure Content Understanding. The frontend uses an **async submit + poll** pattern for audio to avoid this:

1. `POST /api/v1/analyze/audio/submit` → returns `{job_id}` in ~2 s (HTTP 202)
2. Frontend polls `GET /api/v1/analyze/audio/status/{job_id}` every 5 s

If audio still times out, ensure the frontend is using the submit+poll flow (`FileUpload.tsx`) and not the synchronous `/analyze/audio` endpoint.

**General troubleshooting:**

- Check the backend terminal for `Analysis complete` or `Audio job ... completed` logs
- Ensure the backend isn't restarting mid-request (uvicorn `--reload` can cause this)
- Test the backend directly: `curl -X POST http://localhost:8000/api/v1/analyze/image -F 'file=@photo.jpg'`

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

Azure Content Understanding analysis times vary by media type:

- **Images**: typically 20–40 seconds per file.
- **Audio**: can take **10–20+ minutes** for files near the 15-minute duration limit, due to transcription + LLM completion.

The backend retries transient errors (HTTP 429, 503) with exponential back-off up to 3 times. The SDK polling interval is set to 5 seconds (overriding the default 30 s) to detect completion faster.

The frontend uses per-file sequential uploads with different strategies per file type:

- Images are uploaded synchronously through the 600-second proxy.
- Audio files use an async submit + poll pattern that has no timeout ceiling (polls every 5 s for up to 30 minutes).

## Getting Help

If your issue isn't listed here:

1. Check the [GitHub Issues](https://github.com/makautzn/metadata-generator/issues)
2. Review the API logs for correlation IDs (they appear in the `X-Correlation-ID` response header)
3. Open a new issue with reproduction steps and correlation ID
