# REST API

The Metadata Generator exposes a REST API at `http://localhost:8000` during development.

## Base URL

All API endpoints are prefixed with `/api/v1`.

## Health Endpoints

### `GET /health`

Liveness check.

**Response** `200 OK`:

```json
{
  "status": "healthy",
  "service": "metadata-generator-api"
}
```

### `GET /health/ready`

Readiness check.

**Response** `200 OK`:

```json
{
  "status": "ready",
  "service": "metadata-generator-api"
}
```

## Image Analysis

### `POST /api/v1/analyze/image`

Analyze a single image and extract metadata.

**Request**: `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | `file` | Image file (JPEG, PNG, TIFF, WebP). Max 10 MB. |

**Response** `200 OK`:

```json
{
  "file_name": "photo.jpg",
  "content_type": "image/jpeg",
  "file_size": 1234567,
  "metadata": {
    "description": "...",
    "keywords": ["...", "..."],
    "caption": "..."
  },
  "exif": { ... }
}
```

## Audio Analysis

### `POST /api/v1/analyze/audio`

Analyze a single audio file and extract metadata.

**Request**: `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | `file` | Audio file (MP3, WAV, M4A, OGG). Max 10 minutes. |

**Response** `200 OK`:

```json
{
  "file_name": "recording.mp3",
  "content_type": "audio/mpeg",
  "file_size": 2345678,
  "metadata": {
    "description": "...",
    "keywords": ["...", "..."],
    "summary": "..."
  },
  "duration_seconds": 180.5
}
```

## Batch Analysis

### `POST /api/v1/analyze/batch`

Analyze up to 20 files (images and/or audio) in a single request.

**Request**: `multipart/form-data` with multiple `files` fields.

**Response** `200 OK`:

```json
{
  "results": [
    { "status": "success", "file_name": "...", "metadata": { ... } },
    { "status": "error", "file_name": "...", "error": { ... } }
  ],
  "total": 3,
  "successful": 2,
  "failed": 1
}
```

## Interactive Documentation

- **Swagger UI**: [/api/v1/docs](http://localhost:8000/api/v1/docs)
- **ReDoc**: [/api/v1/redoc](http://localhost:8000/api/v1/redoc)
