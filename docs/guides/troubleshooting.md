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

Check that `ALLOWED_ORIGINS` in your `.env` includes the frontend URL:

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

### API requests fail in development

Ensure the backend server is running on port 8000 and that `NEXT_PUBLIC_API_URL` is set:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

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

### `401 Unauthorized`

- Verify `AZURE_CONTENT_UNDERSTANDING_ENDPOINT` is correct
- Verify `AZURE_CONTENT_UNDERSTANDING_KEY` is valid and not expired
- Ensure the key matches the endpoint's resource

### Timeout errors

Azure Content Understanding analysis can take several seconds per file. For batch processing, expect longer total times. The timeout is configurable via environment variables.

## Getting Help

If your issue isn't listed here:

1. Check the [GitHub Issues](https://github.com/makautzn/metadata-generator/issues)
2. Review the API logs for correlation IDs (they appear in the `X-Correlation-ID` response header)
3. Open a new issue with reproduction steps and correlation ID
