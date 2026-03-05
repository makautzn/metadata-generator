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
  "file_size": 2048576,
  "mime_type": "image/jpeg",
  "description": "Ein Tennisspieler schlägt ...",
  "keywords": ["Tennis", "Sport", "Rasen", "Rafael Nadal"],
  "caption": "Rafael Nadal bei den French Open.",
  "exif": { "camera_model": "Canon EOS R5", "date_taken": "2025-06-15" },
  "processing_time_ms": 3200
}
```

## Audio Analysis

### `POST /api/v1/analyze/audio`

Analyze a single audio file and extract metadata (synchronous). Suitable for short files or direct API use. For the web frontend, prefer the async submit + poll endpoints below.

**Request**: `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | `file` | Audio file (MP3, WAV, M4A, OGG). Max 15 minutes. |

**Response** `200 OK`:

```json
{
  "file_name": "interview.mp3",
  "file_size": 5242880,
  "mime_type": "audio/mpeg",
  "description": "Ein Interview über die aktuelle Wirtschaftslage ...",
  "keywords": ["Wirtschaft", "Interview", "Konjunktur"],
  "summary": "Das Interview behandelt die aktuelle Konjunkturentwicklung.",
  "duration_seconds": 342.5,
  "processing_time_ms": 8500
}
```

### `POST /api/v1/analyze/audio/submit`

Submit an audio file for asynchronous analysis. Returns a job ID immediately (HTTP 202) — use the status endpoint to poll for results. This is the **recommended** approach for the web frontend because audio analysis can take 10–20+ minutes.

**Request**: `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | `file` | Audio file (MP3, WAV, M4A, OGG). Max 15 minutes. |

**Response** `202 Accepted`:

```json
{
  "job_id": "cb47497598684b3d974577ba504f7aeb",
  "status": "accepted"
}
```

### `GET /api/v1/analyze/audio/status/{job_id}`

Poll the status of an async audio analysis job.

**Response** `200 OK` (processing):

```json
{
  "job_id": "cb47497598684b3d974577ba504f7aeb",
  "status": "processing",
  "result": null,
  "error": null
}
```

**Response** `200 OK` (completed):

```json
{
  "job_id": "cb47497598684b3d974577ba504f7aeb",
  "status": "completed",
  "result": {
    "file_name": "interview.mp3",
    "file_size": 5242880,
    "mime_type": "audio/mpeg",
    "description": "Ein Interview über die aktuelle Wirtschaftslage ...",
    "keywords": ["Wirtschaft", "Interview", "Konjunktur"],
    "summary": "Das Interview behandelt die aktuelle Konjunkturentwicklung.",
    "duration_seconds": 342.5,
    "processing_time_ms": 850000
  },
  "error": null
}
```

**Response** `200 OK` (failed):

```json
{
  "job_id": "cb47497598684b3d974577ba504f7aeb",
  "status": "failed",
  "result": null,
  "error": "Analyse fehlgeschlagen: Azure service error"
}
```

**Response** `404 Not Found`:

```json
{
  "detail": "Job cb474975... not found or expired"
}
```

!!! note "Job Expiry"
    Completed and failed jobs are automatically removed from the in-memory store after **30 minutes**.

## Batch Analysis

### `POST /api/v1/analyze/batch`

Analyze up to 20 files (images and/or audio) in a single request. Files are processed concurrently (up to 5 at a time).

!!! note "Frontend uses per-file uploads"
    The web frontend does **not** use the batch endpoint. It uploads files one at a time (images via `/analyze/image`, audio via `/analyze/audio/submit`) to avoid proxy timeouts with long-running audio analysis. The batch endpoint is available for direct API consumers.

**Request**: `multipart/form-data` with multiple `files` fields.

**Response** `200 OK`:

```json
{
  "results": [
    {
      "file_name": "photo.jpg",
      "file_index": 0,
      "status": "success",
      "file_type": "image",
      "metadata": {
        "file_name": "photo.jpg",
        "file_size": 2048576,
        "mime_type": "image/jpeg",
        "description": "...",
        "keywords": ["..."],
        "caption": "...",
        "exif": {},
        "processing_time_ms": 3200
      },
      "error": null
    },
    {
      "file_name": "broken.xyz",
      "file_index": 1,
      "status": "error",
      "file_type": "unknown",
      "metadata": null,
      "error": "Unsupported file type"
    }
  ],
  "total_files": 2,
  "successful": 1,
  "failed": 1,
  "total_processing_time_ms": 3450
}
```

## Interactive Documentation

- **Swagger UI**: [/api/v1/docs](http://localhost:8000/api/v1/docs)
- **ReDoc**: [/api/v1/redoc](http://localhost:8000/api/v1/redoc)
