# How Azure Content Understanding Powers Metadata Extraction

This document provides a step-by-step explanation of how the **Azure Content Understanding** service is used to implement both the **Image Metadata Extraction** ("Bildverschlagwortung") and **Audio Metadata Extraction** ("Audio Analyse") features.

---

## 1. Overview

Azure Content Understanding is an AI service that analyses binary media (images, audio, documents) and returns structured metadata. In this project it is accessed through the Python SDK `azure-ai-contentunderstanding` and wrapped by a dedicated service class (`AzureContentUnderstandingService`). Two **custom analyzers** are registered on the Azure side — one for images, one for audio — each configured to return German-language metadata fields.

---

## 2. Custom Analyzers in Azure

Before any code runs, two custom analyzers must exist in the Azure Content Understanding resource:

| Analyzer ID | Base Analyzer | Completion Model | Purpose |
|---|---|---|---|
| `imageMetadataExtractor` | `prebuilt-image` | `gpt-4.1-mini` | Extracts Description, Caption, and Keywords from images |
| `audioMetadataExtractor` | `prebuilt-audio` | `gpt-4.1-mini` | Extracts Description, Summary, and Keywords from audio |

Both analyzers are created on API version **`2025-11-01`** and use camelCase IDs (hyphenated names are rejected by this API version). Each analyzer defines custom field prompts that instruct the model to produce output **in German**.

!!! note
    The `models.completion` property (`gpt-4.1-mini`) is **required** on API version `2025-11-01`. Omitting it causes a `ModelNotFound` error.

---

## 3. Application Configuration

The backend needs two environment variables to connect to the Azure service:

| Variable | Description |
|---|---|
| `AZURE_CONTENT_UNDERSTANDING_ENDPOINT` | The HTTPS endpoint of the Azure Content Understanding resource |
| `AZURE_CONTENT_UNDERSTANDING_KEY` | An API key for authentication |

These are loaded at startup via Pydantic Settings (`app/core/config.py` → `Settings`) and injected through FastAPI's dependency injection system (`app/core/dependencies.py`).

---

## 4. Step-by-Step: Image Metadata Extraction

### Step 1 — User Uploads an Image

The user sends a `POST` request to `/api/v1/analyze/image` with a multipart file upload. Supported formats: **JPEG, PNG, TIFF, WebP** (max **10 MB**).

### Step 2 — File Validation

The `image` router reads the file bytes and runs two checks:

1. **Size validation** — rejects files > 10 MB with HTTP 413.
2. **Content-type validation** — inspects the file's magic bytes and declared MIME type; rejects unsupported formats with HTTP 422.

### Step 3 — EXIF Extraction

Before calling Azure, the router extracts **EXIF metadata** (camera model, GPS coordinates, date taken, exposure, etc.) from the raw image bytes using a local utility (`app/utils/exif_extraction.py`). This runs entirely on the server — no cloud call needed.

### Step 4 — Azure Content Understanding Analysis

The router calls `cu_service.analyze_image(file_bytes, detected_mime)`, which triggers the following sequence inside `AzureContentUnderstandingService`:

1. A fresh `ContentUnderstandingClient` is created using the configured endpoint and API key.
2. `client.begin_analyze_binary()` is called with:
   - `analyzer_id = "imageMetadataExtractor"`
   - `binary_input = <raw image bytes>`
   - `content_type = <detected MIME type>`
3. This returns an async **poller**. The service awaits `poller.result()` to obtain the `AnalyzeResult`.
4. If a transient error occurs (HTTP 429 or 503), the service retries up to 3 times with exponential back-off (1 s → 2 s → 4 s).

### Step 5 — Parsing the Azure Response

The `AnalyzeResult` contains a list of `contents`, each with a `fields` dictionary of `ContentField` objects. The parser (`_parse_image_result`) extracts:

| Field Name | Extraction Logic | Fallback |
|---|---|---|
| **Description** | `fields["Description"].value` | First 500 characters of the result's markdown |
| **Caption** | `fields["Caption"].value` | First 200 characters of the description |
| **Keywords** | Each item in `fields["Keywords"].value` list → `item.value` (plain string) | Salient words parsed from the markdown; ultimate fallback: `["Allgemein", "Inhalt", "Medium"]` |

Keywords containing markdown artifact characters (`[]`, `()`, `#`, `|`, `/`) are filtered out.

### Step 6 — Response Assembly

The router combines the AI-generated metadata with the locally extracted EXIF data into an `ImageMetadataResponse`:

```json
{
  "file_name": "photo.jpg",
  "file_size": 2048576,
  "mime_type": "image/jpeg",
  "description": "Ein Tennisspieler schlägt ...",
  "keywords": ["Tennis", "Sport", "Rasen"],
  "caption": "Tennisspieler bei den French Open.",
  "exif": { "camera_model": "Canon EOS R5", "date_taken": "2025-06-15", ... },
  "processing_time_ms": 3200
}
```

---

## 5. Step-by-Step: Audio Metadata Extraction

### Step 1 — User Uploads an Audio File

The user sends a `POST` request to `/api/v1/analyze/audio` with a multipart file upload. Supported formats: **MP3, WAV, M4A, OGG** (max **15 minutes** duration).

### Step 2 — File Validation

The `audio` router reads the file bytes and validates:

1. **Format** — checks the declared MIME type and magic bytes against allowed types.
2. **Duration** — determines the audio length and rejects files exceeding 15 minutes (HTTP 422).

Both checks are performed by `validate_audio_upload()` in `app/utils/audio_utils.py`.

### Step 3 — Azure Content Understanding Analysis

The router calls `cu_service.analyze_audio(file_bytes, mime_type)`, which follows the same pattern as image analysis:

1. Creates a `ContentUnderstandingClient`.
2. Calls `client.begin_analyze_binary()` with:
   - `analyzer_id = "audioMetadataExtractor"`
   - `binary_input = <raw audio bytes>`
   - `content_type = <detected MIME type>`
3. Awaits the poller result.
4. Retries transient errors with exponential back-off.

### Step 4 — Parsing the Azure Response

The parser (`_parse_audio_result`) extracts from the `AnalyzeResult`:

| Field Name | Extraction Logic | Fallback |
|---|---|---|
| **Description** | `fields["Description"].value` | First 500 characters of the result's markdown |
| **Summary** | `fields["Summary"].value`, then truncated to the first sentence via `_truncate_to_first_sentence()` | First 200 characters of the description |
| **Keywords** | Same logic as image keywords (list of `ContentField` items → plain strings) | Markdown word extraction or default keywords |

!!! tip
    The `_truncate_to_first_sentence()` safeguard ensures the summary stays at one sentence even if the Azure analyzer returns a longer paragraph.

### Step 5 — Response Assembly

The metadata is returned as an `AudioMetadataResponse`:

```json
{
  "file_name": "interview.mp3",
  "file_size": 5242880,
  "mime_type": "audio/mpeg",
  "description": "Ein Interview über die aktuelle Wirtschaftslage ...",
  "keywords": ["Wirtschaft", "Interview", "Konjunktur"],
  "summary": "Das Interview behandelt die aktuelle Konjunkturentwicklung in Deutschland.",
  "duration_seconds": 342.5,
  "processing_time_ms": 8500
}
```

---

## 6. Shared Infrastructure

Both features share the following cross-cutting concerns implemented in `AzureContentUnderstandingService`:

### Retry with Exponential Back-off

Transient HTTP errors (429 — rate-limited, 503 — service unavailable) are retried up to 3 times. Wait times double on each attempt: 1 s → 2 s → 4 s. After exhausting retries, a `TransientError` is raised.

### Client Lifecycle

A new `ContentUnderstandingClient` is created per request (via `async with`) to avoid connection-sharing issues in concurrent workloads. The client is automatically closed when the context manager exits.

### Error Hierarchy

All service errors inherit from `ContentUnderstandingError`:

- `ConfigurationError` — missing endpoint or key.
- `TransientError` — retries exhausted on a recoverable error.
- `AnalysisServiceError` — non-retryable Azure errors or empty results.

### Dependency Injection

The service is instantiated via `get_content_understanding_service()` in `app/core/dependencies.py` and injected into route handlers using FastAPI's `Depends()`. In tests, this dependency is overridden with a mock service.

---

## 7. Data Flow Diagram

```
┌──────────┐      POST /api/v1/analyze/{image|audio}      ┌──────────────┐
│  Client  │ ────────────── file upload ──────────────────▶│  FastAPI     │
│  (Web)   │                                               │  Router      │
└──────────┘                                               └──────┬───────┘
                                                                  │
                                           ┌──────────────────────┼─────────────────┐
                                           │                      │                 │
                                           ▼                      ▼                 ▼
                                   ┌──────────────┐     ┌─────────────────┐  ┌────────────┐
                                   │  Validate    │     │  EXIF Extract   │  │  Validate  │
                                   │  Size/Type   │     │  (image only)   │  │  Duration  │
                                   └──────┬───────┘     └────────┬────────┘  │ (audio)    │
                                          │                      │           └─────┬──────┘
                                          ▼                      │                 │
                               ┌─────────────────────────────────┴─────────────────┘
                               │
                               ▼
                    ┌────────────────────────────┐
                    │ AzureContentUnderstanding  │
                    │       Service              │
                    ├────────────────────────────┤
                    │ begin_analyze_binary()     │
                    │   analyzer_id:             │
                    │   • imageMetadataExtractor  │
                    │   • audioMetadataExtractor  │
                    │                            │
                    │ await poller.result()      │
                    │ (with retry on 429/503)    │
                    └──────────┬─────────────────┘
                               │
                               ▼
                    ┌────────────────────────────┐
                    │  Azure Content             │
                    │  Understanding (Cloud)     │
                    │                            │
                    │  Custom Analyzer +         │
                    │  gpt-4.1-mini completion   │
                    └──────────┬─────────────────┘
                               │
                               ▼
                    ┌────────────────────────────┐
                    │  Parse AnalyzeResult       │
                    │  → Description, Keywords,  │
                    │    Caption / Summary       │
                    └──────────┬─────────────────┘
                               │
                               ▼
                    ┌────────────────────────────┐
                    │  Return JSON Response      │
                    │  (ImageMetadataResponse    │
                    │   or AudioMetadataResponse)│
                    └────────────────────────────┘
```

---

## 8. Key Lessons from E2E Testing

| # | Issue | Resolution |
|---|-------|-----------|
| 1 | SDK defaults to API version `2025-11-01`; analyzers created on `2024-12-01-preview` were invisible → `ModelNotFound`. | Recreated analyzers on `2025-11-01` with explicit `models.completion: gpt-4.1-mini`. |
| 2 | Hyphenated analyzer IDs (e.g. `audio-metadata-extractor`) rejected by `2025-11-01`. | Switched to camelCase: `audioMetadataExtractor`, `imageMetadataExtractor`. |
| 3 | Keywords returned as `ContentField` objects, not plain strings. | Extract via `item.value` / `getattr(k, "value", k)`. |
| 4 | Audio summary was a full paragraph instead of one sentence. | Updated analyzer prompt + added `_truncate_to_first_sentence()` server-side safeguard. |
| 5 | `min_length=3` on keywords too strict for simple content. | Relaxed to `min_length=1`. |
| 6 | Markdown artifacts (`[]`, `#`, `|`) appeared in keyword lists. | Added filter in `_extract_keywords()` to discard tainted entries. |
