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

Analyze a single audio file and extract metadata.

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

## Batch Analysis

### `POST /api/v1/analyze/batch`

Analyze up to 20 files (images and/or audio) in a single request. Files are processed concurrently (up to 5 at a time).

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
