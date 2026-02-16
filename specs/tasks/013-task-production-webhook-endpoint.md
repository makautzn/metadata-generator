# 013 — Production Webhook Endpoint

## Description

Implement the production webhook API that external systems can call to trigger metadata extraction. The webhook accepts file references (URLs), authenticates via API key, supports batch requests, and delivers results via callback (push) to a caller-provided URL. Covers requirements HOOK-1 through HOOK-15.

## Dependencies

- **001** — Backend API project scaffolding
- **004** — Azure Content Understanding integration service
- **005** — Image metadata extraction API (reuses the analysis logic)
- **006** — Audio metadata extraction API (reuses the analysis logic)

## Technical Requirements

### Webhook Endpoint

- **Route**: `POST /api/v1/webhook/analyze`
- **Content-Type**: `application/json`
- **Authentication**: API key required via `X-API-Key` request header

### Request Model

```
WebhookRequest:
  files: list[FileReference]       # 1 or more file references (batch support)
  callback_url: str                # URL to POST results to upon completion

FileReference:
  url: str                         # Publicly accessible URL or storage path to the file
  file_type: "image" | "audio"     # Explicit type declaration
  reference_id: str | None         # Optional caller-defined ID for correlation
```

### Processing Flow

1. Validate the API key against configured allowed keys
2. Validate the request body (file references, callback URL)
3. Return `202 Accepted` immediately with a job ID
4. Process files asynchronously in the background:
   a. Download each file from its URL
   b. Validate file format, size (images ≤ 10 MB), and duration (audio ≤ 10 min)
   c. Route to image or audio analysis service
   d. Collect all results
5. POST results to the `callback_url` once all files are processed

### Callback Payload

```
WebhookCallbackPayload:
  job_id: str
  status: "completed" | "partial" | "failed"
  results: list[WebhookFileResult]
  total_files: int
  successful: int
  failed: int
  processing_time_ms: int

WebhookFileResult:
  reference_id: str | None
  file_url: str
  file_type: "image" | "audio"
  status: "success" | "error"
  metadata: ImageMetadataResponse | AudioMetadataResponse | None
  error: AnalysisError | None
```

### API Key Authentication

- API keys are stored in configuration (environment variable or secret store)
- Support multiple valid API keys for different consumers
- Missing or invalid API key returns `401 Unauthorized` with error body
- Log authentication failures (key hash only, not the key itself)

### Idempotency

- The endpoint must be idempotent for the same set of file references
- Processing the same `file_url` multiple times produces the same metadata output

### Background Processing

- Use FastAPI `BackgroundTasks` or a dedicated async task runner for background processing
- Processing must complete within 15 minutes per file
- If callback delivery fails, log the failure with retry information

### Error Handling

- Invalid callback URL format → `422` response
- File download failure → per-file error in callback results
- Azure service failure → per-file error in callback results
- Callback delivery failure → log error, no retry in PoC (document as limitation)

## Acceptance Criteria

- [x] `POST /api/v1/webhook/analyze` with valid API key and file references returns `202` with job ID
- [x] Results are delivered to the callback URL as a POST request
- [x] Batch requests with multiple files are processed and all results delivered
- [x] Missing API key returns `401`
- [x] Invalid API key returns `401`
- [x] Invalid request body returns `422` with structured error
- [x] Per-file errors (download failure, invalid format) appear in callback results without failing the batch
- [x] Callback payload follows the documented schema
- [x] Same file URL processed twice produces the same metadata
- [x] Processing completes within 15 minutes per file
- [x] Endpoint appears in OpenAPI docs at `/docs`

## Testing Requirements

- Unit test: valid request with API key returns 202
- Unit test: missing API key returns 401
- Unit test: invalid API key returns 401
- Unit test: request with empty files list returns 422
- Unit test: request with invalid callback URL returns 422
- Unit test: batch with 3 file references is accepted
- Unit test: file download failure produces per-file error in result
- Unit test: callback payload matches expected schema
- Unit test: job ID is unique per request
- Integration test: end-to-end flow — request → background processing → callback delivery (with mocked Azure service and callback endpoint)
- Integration test: idempotency — same request produces same results
- Coverage: ≥ 85%
