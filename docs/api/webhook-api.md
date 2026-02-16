# Webhook API

The webhook endpoint enables external systems (CMS, DAM) to trigger metadata extraction programmatically.

## Authentication

All webhook requests must include an API key in the `X-API-Key` header.

## Endpoint

### `POST /api/v1/webhook/analyze`

Submit files for asynchronous metadata extraction.

**Headers**:

| Header | Description |
|--------|-------------|
| `X-API-Key` | API key for authentication |
| `Content-Type` | `application/json` |

**Request Body**:

```json
{
  "files": [
    {
      "url": "https://storage.example.com/image.jpg",
      "type": "image"
    },
    {
      "url": "https://storage.example.com/recording.mp3",
      "type": "audio"
    }
  ],
  "callback_url": "https://cms.example.com/api/metadata-callback",
  "request_id": "optional-idempotency-key"
}
```

**Response** `202 Accepted`:

```json
{
  "request_id": "uuid-v4",
  "status": "accepted",
  "file_count": 2
}
```

## Callback Payload

When processing completes, the API sends a POST request to the `callback_url`:

```json
{
  "request_id": "uuid-v4",
  "status": "completed",
  "results": [
    {
      "url": "https://storage.example.com/image.jpg",
      "type": "image",
      "status": "success",
      "metadata": {
        "description": "...",
        "keywords": ["...", "..."],
        "caption": "..."
      }
    }
  ],
  "completed_at": "2026-01-15T10:30:00Z"
}
```

## Error Handling

| HTTP Status | Meaning |
|-------------|---------|
| `202` | Request accepted for processing |
| `401` | Missing or invalid API key |
| `422` | Validation error (invalid URL, unsupported type) |
| `429` | Rate limit exceeded |

## SLA

- Maximum processing latency: **15 minutes** per file
- Timeout: files not processed within 15 minutes are reported as errors in the callback
