# 007 — File Upload API Endpoint

## Description

Implement a unified file upload API endpoint that accepts multiple files (images and/or audio) in a single request, dispatches each file to the appropriate analysis endpoint (image or audio), and returns aggregated results. This is the primary endpoint consumed by the frontend's multi-file upload. Covers requirements WEB-2, WEB-5, WEB-6.

## Dependencies

- **005** — Image metadata extraction API
- **006** — Audio metadata extraction API

## Technical Requirements

### API Endpoint

- **Route**: `POST /api/v1/analyze/batch`
- **Content-Type**: `multipart/form-data`
- **Request**: Multiple files in a single request (up to 20 files)
- **Response**: JSON array of results, one per file, preserving upload order

### Request Validation

- Accept up to 20 files per request
- Reject requests with more than 20 files → return `422` with clear message
- Each file is individually validated (type, size/duration) — invalid files produce per-file error entries, not a full request failure
- Total request size limit should be configured (recommended: 200 MB to accommodate 20 × 10 MB images)

### Processing

- Process files concurrently using `asyncio.gather()` or `asyncio.Semaphore()` for controlled parallelism
- Use a configurable concurrency limit to avoid overwhelming the Azure service
- Each file is routed to the image or audio analysis service based on MIME type
- Track per-file processing time

### Response Model

Define a Pydantic response model:

```
BatchAnalysisResponse:
  results: list[FileAnalysisResult]
  total_files: int
  successful: int
  failed: int
  total_processing_time_ms: int

FileAnalysisResult:
  file_name: str
  file_index: int              # preserves upload order
  status: "success" | "error"
  file_type: "image" | "audio"
  metadata: ImageMetadataResponse | AudioMetadataResponse | None
  error: AnalysisError | None
```

### Error Handling

- Individual file failures do not fail the entire batch
- Each failed file gets an error entry in the results array with error code and message
- The response always returns 200 for the batch, with per-file status indicators
- Log batch-level summary (total, success, failed) and individual errors

## Acceptance Criteria

- [x] `POST /api/v1/analyze/batch` with 5 mixed files returns 200 with 5 results
- [x] Results are ordered by `file_index` matching upload order
- [x] Image files produce `ImageMetadataResponse` results
- [x] Audio files produce `AudioMetadataResponse` results
- [x] An invalid file in a batch produces an error entry without failing other files
- [x] Requests with > 20 files return 422
- [x] `total_files`, `successful`, and `failed` counts are accurate
- [x] Files are processed concurrently (total time < sum of individual times)
- [x] Endpoint appears in OpenAPI docs at `/docs`

## Testing Requirements

- Unit test: batch with 3 valid images returns 3 success results
- Unit test: batch with 2 valid audio files returns 2 success results
- Unit test: mixed batch (images + audio) returns correct file_type per result
- Unit test: batch with 1 invalid file returns 1 error + N-1 successes
- Unit test: batch with > 20 files returns 422
- Unit test: results preserve upload order via file_index
- Unit test: summary counts (total, successful, failed) are correct
- Unit test: empty batch (0 files) returns 422 or appropriate error
- Integration test: concurrent processing completes faster than sequential
- Coverage: ≥ 85%
