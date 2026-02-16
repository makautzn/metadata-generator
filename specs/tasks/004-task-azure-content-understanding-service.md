# 004 — Azure Content Understanding Integration Service

## Description

Implement a backend service that wraps the Azure Content Understanding API, providing a reusable abstraction for analyzing images and audio files. This service encapsulates authentication, request construction, response parsing, error handling, and retry logic. It is consumed by the image and audio metadata extraction endpoints.

## Dependencies

- **001** — Backend API project scaffolding (project structure must exist)

## Technical Requirements

### Service Interface

Define an abstract interface (protocol or ABC) for the content understanding service with methods:

- `analyze_image(file_bytes, content_type) → ImageAnalysisResult` — Sends an image to Azure Content Understanding and returns structured analysis
- `analyze_audio(file_bytes, content_type) → AudioAnalysisResult` — Sends an audio file to Azure Content Understanding and returns structured analysis

### Pydantic Models

Define response models in `app/models/`:

- `ImageAnalysisResult`: description (str), keywords (list[str]), caption (str)
- `AudioAnalysisResult`: description (str), keywords (list[str]), summary (str)
- `AnalysisError`: error_code (str), message (str)

All text output fields must be in German — the system prompt / analyzer configuration must specify German as the output language.

### Service Implementation

- Implement as an async service class in `app/services/`
- Use the Azure Content Understanding Python SDK or REST API
- Authenticate using Azure credentials (API key from configuration, with managed identity as future option)
- Implement retry logic with exponential backoff for transient errors (HTTP 429, 503)
- Handle and wrap all Azure SDK exceptions into application-specific error types
- Log analysis requests and responses (excluding file content) with correlation IDs

### Configuration

- Add Azure Content Understanding settings to the Pydantic Settings config:
  - `AZURE_CONTENT_UNDERSTANDING_ENDPOINT`
  - `AZURE_CONTENT_UNDERSTANDING_KEY`
- Update `.env.example` with the new variables

### Dependency Injection

- Register the service in FastAPI's dependency injection system
- Provide a factory function that creates and returns the service instance
- Support dependency override for testing

## Acceptance Criteria

- [x] Service successfully authenticates with Azure Content Understanding
- [x] `analyze_image()` returns a populated `ImageAnalysisResult` with description, keywords, and caption in German
- [x] `analyze_audio()` returns a populated `AudioAnalysisResult` with description, keywords, and summary in German
- [x] Invalid credentials produce a clear, logged error — not an unhandled exception
- [x] Transient Azure errors trigger retry with exponential backoff (up to 3 retries)
- [x] Non-transient errors are wrapped in `AnalysisError` with appropriate error code
- [x] Service is injectable via FastAPI `Depends()`
- [x] Configuration values load from environment variables

## Testing Requirements

- Unit test: `analyze_image()` returns expected model when Azure API returns valid response (mocked)
- Unit test: `analyze_audio()` returns expected model when Azure API returns valid response (mocked)
- Unit test: retry logic triggers on 429 status and succeeds on subsequent attempt (mocked)
- Unit test: non-retryable error produces `AnalysisError` with correct error code
- Unit test: service raises configuration error when endpoint/key are missing
- Unit test: all output fields are non-empty strings
- Unit test: keywords list contains between 3 and 15 items
- Integration test: service can be resolved from FastAPI dependency injection
- Coverage: ≥ 85%

---

## E2E Testing Findings

The following issues were identified and resolved during end-to-end testing (2026-02-16):

| Finding | Resolution |
|---------|-----------|
| `aiohttp` is required at runtime by the Azure Content Understanding SDK but was not listed as a project dependency. | Added `aiohttp` to `pyproject.toml`. |
| Azure endpoint URL must be the base URL (e.g. `https://<resource>.services.ai.azure.com`). Project-scoped URLs with `/api/projects/<name>` path do not work with `AzureKeyCredential` / `Ocp-Apim-Subscription-Key` authentication. | Documented correct endpoint format; service validates and strips trailing paths. |
| The SDK defaults to API version `2025-11-01` (found in `_configuration.py`). Custom analyzers created on `2024-12-01-preview` are invisible to the SDK, causing `ModelNotFound` (404) errors. | Custom analyzers must be created on API version `2025-11-01`. |
| On `2025-11-01`, custom analyzer IDs cannot contain hyphens. | Use camelCase identifiers (e.g. `imageMetadataExtractor`, `audioMetadataExtractor`). |
| On `2025-11-01`, custom analyzers require `models.completion` to be specified (e.g. `gpt-4.1-mini`). | Added `models: {completion: "gpt-4.1-mini"}` to analyzer creation payloads. |
| Keywords array field: each element in `ContentField.value` is itself a `ContentField` object. `str(k)` produces the dict repr (`{'type': 'string', 'valueString': '...'}`). | Keyword extraction now reads `k.value` (the inner string) via `getattr(k, "value", k)`. |
| `min_length=3` on keywords was too strict — Azure sometimes returns fewer keywords for simple content. | Relaxed to `min_length=1` in both `ImageAnalysisResult` and `AudioAnalysisResult`. |
| Markdown-based keyword fallback captured artifacts like `image](pages/1`. | Added filter to exclude tokens containing `[]()#\|/` characters. |
