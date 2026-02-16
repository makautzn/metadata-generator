# Quick Start

Get the Metadata Generator running locally in under 5 minutes.

## 1. Start the Backend

```bash
cd MetadataGenerator.Api
cp .env.example .env
# Add your Azure credentials to .env
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify the API is running:

```bash
curl http://localhost:8000/health
# {"status": "healthy", "service": "metadata-generator-api"}
```

## 2. Start the Frontend

```bash
cd MetadataGenerator.Web
cp .env.local.example .env.local
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 3. Upload Files

1. Click the upload area or drag and drop files.
2. Select images (JPEG, PNG, TIFF, WebP) and/or audio files (MP3, WAV, M4A, OGG).
3. Click **Analysieren** to start processing.
4. View the generated metadata in the tile grid.
5. Copy individual fields or export all results as CSV/JSON.

## API Documentation

Once the backend is running, visit:

- **Swagger UI**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **ReDoc**: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)
