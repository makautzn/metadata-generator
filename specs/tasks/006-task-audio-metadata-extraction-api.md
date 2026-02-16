# 006 — Audio Metadata Extraction API

## Description

Implement the backend API endpoint for audio metadata extraction. This endpoint receives an uploaded audio file, validates it (format and duration), calls the Azure Content Understanding service for AI-generated metadata (description, keywords, one-sentence summary), and returns a structured response. Covers requirements AUD-1 through AUD-10.

## Dependencies

- **001** — Backend API project scaffolding
- **004** — Azure Content Understanding integration service

## Technical Requirements

### API Endpoint

- **Route**: `POST /api/v1/analyze/audio`
- **Content-Type**: `multipart/form-data`
- **Request**: Single audio file upload
- **Response**: JSON with AI-generated metadata

### File Validation

- Accept: MP3 (`audio/mpeg`), WAV (`audio/wav`), M4A (`audio/mp4`, `audio/x-m4a`), OGG (`audio/ogg`)
- Reject files with unsupported MIME types → return `422` with human-readable error
- Validate audio duration does not exceed 10 minutes → return `422` with error message indicating duration limit
- Use an audio processing library (e.g., `mutagen`, `pydub`, or `ffprobe`) to determine duration

### AI Metadata Generation

- Call the Azure Content Understanding service (`analyze_audio`) to generate:
  - Full-text description (minimum 2 sentences, in German)
  - Keywords / tags (3–15 items, in German)
  - One-sentence summary (Kurz-Zusammenfassung, in German)

### Response Model

Define a Pydantic response model:

```
AudioMetadataResponse:
  file_name: str
  file_size: int (bytes)
  mime_type: str
  duration_seconds: float
  description: str
  keywords: list[str]
  summary: str
  processing_time_ms: int
```

### Error Handling

- Return structured error responses for all failure cases
- Provide clear error messages distinguishing between format errors and duration limit violations
- Log errors with file name, correlation ID, and error details

## Acceptance Criteria

- [x] `POST /api/v1/analyze/audio` with a valid MP3 (≤ 10 min) returns 200 with all metadata fields populated
- [x] Description is at least 2 sentences and in German
- [x] Keywords contain between 3 and 15 items
- [x] Summary is exactly one sentence
- [x] WAV, M4A, and OGG formats are accepted and processed successfully
- [x] Audio files exceeding 10 minutes return `422` with clear duration error
- [x] Unsupported file types return `422` with clear format error
- [x] `duration_seconds` accurately reflects the audio file length
- [x] Response includes `processing_time_ms` as a positive integer
- [x] Endpoint appears in OpenAPI docs at `/docs`

## Testing Requirements

- Unit test: valid MP3 upload (< 10 min) returns `AudioMetadataResponse` with all fields
- Unit test: valid WAV upload returns successful response
- Unit test: valid OGG upload returns successful response
- Unit test: audio file exceeding 10 minutes returns 422 with duration error
- Unit test: unsupported file type returns 422 with format error
- Unit test: duration_seconds is accurate (within ±1 second tolerance)
- Unit test: summary is a single sentence (no line breaks, ends with period)
- Unit test: keywords count is between 3 and 15
- Integration test: end-to-end upload and response (with mocked Azure service)
- Coverage: ≥ 85%
