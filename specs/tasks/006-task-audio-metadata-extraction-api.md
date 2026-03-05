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
- Validate audio duration does not exceed 15 minutes → return `422` with error message indicating duration limit
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

- [x] `POST /api/v1/analyze/audio` with a valid MP3 (≤ 15 min) returns 200 with all metadata fields populated
- [x] Description is at least 2 sentences and in German
- [x] Keywords contain between 3 and 15 items
- [x] Summary is exactly one sentence
- [x] WAV, M4A, and OGG formats are accepted and processed successfully
- [x] Audio files exceeding 15 minutes return `422` with clear duration error
- [x] Unsupported file types return `422` with clear format error
- [x] `duration_seconds` accurately reflects the audio file length
- [x] Response includes `processing_time_ms` as a positive integer
- [x] Endpoint appears in OpenAPI docs at `/docs`

## Testing Requirements

- Unit test: valid MP3 upload (< 15 min) returns `AudioMetadataResponse` with all fields
- Unit test: valid WAV upload returns successful response
- Unit test: valid OGG upload returns successful response
- Unit test: audio file exceeding 15 minutes returns 422 with duration error
- Unit test: unsupported file type returns 422 with format error
- Unit test: duration_seconds is accurate (within ±1 second tolerance)
- Unit test: summary is a single sentence (no line breaks, ends with period)
- Unit test: keywords count is between 3 and 15
- Integration test: end-to-end upload and response (with mocked Azure service)
- Coverage: ≥ 85%

---

## E2E Testing Findings

The following issues were identified and resolved during end-to-end testing (2026-02-16):

| Finding | Resolution |
|---------|------------|
| Maximum audio duration of 10 minutes was too short for real editorial audio clips. | Extended `MAX_AUDIO_DURATION_SECONDS` from 600 to 900 (15 minutes). Updated test mock values from 700 s to 1000 s. |
| Audio one-sentence summary was returning a full paragraph. | Updated Azure `audioMetadataExtractor` analyzer prompt to enforce "exactly ONE sentence, max 30 words". Added backend `_truncate_to_first_sentence()` safeguard that splits on sentence-ending punctuation. |

---

## Async Submit + Poll Architecture (Added 2026-03-05)

Audio analysis on Azure Content Understanding can take 10–20+ minutes for files near the 15-minute duration limit. This exceeds any practical proxy timeout, so the backend now provides two additional endpoints:

| Endpoint | Method | Purpose |
|----------|--------|----------|
| `/api/v1/analyze/audio/submit` | POST | Accepts the audio file, validates it, starts a background task, returns `{job_id}` (HTTP 202) |
| `/api/v1/analyze/audio/status/{job_id}` | GET | Returns current job status (`processing`, `completed`, `failed`) with result or error |

### Key details

- Background task runs via `asyncio.create_task()` in the FastAPI process.
- In-memory job store (`_jobs` dict) with 30-minute TTL — sufficient for single-process PoC.
- The SDK `polling_interval` is set to **5 seconds** (overriding the default 30 s) to detect completion faster.
- The frontend polls every 5 seconds for up to 30 minutes (360 attempts).
- The synchronous `POST /api/v1/analyze/audio` endpoint is kept for backwards compatibility / direct API use.

### New response models

```
AudioJobSubmitResponse:
  job_id: str
  status: "accepted"

AudioJobStatusResponse:
  job_id: str
  status: "processing" | "completed" | "failed"
  result: AudioMetadataResponse | null
  error: str | null
```
