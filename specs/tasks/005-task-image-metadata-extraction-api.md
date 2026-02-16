# 005 — Image Metadata Extraction API

## Description

Implement the backend API endpoint for image metadata extraction. This endpoint receives an uploaded image file, validates it, extracts EXIF metadata, calls the Azure Content Understanding service for AI-generated metadata (description, keywords, caption), and returns a combined response. Covers requirements IMG-1 through IMG-9.

## Dependencies

- **001** — Backend API project scaffolding
- **004** — Azure Content Understanding integration service

## Technical Requirements

### API Endpoint

- **Route**: `POST /api/v1/analyze/image`
- **Content-Type**: `multipart/form-data`
- **Request**: Single image file upload
- **Response**: JSON with AI-generated metadata and EXIF data

### File Validation

- Accept: JPEG (`image/jpeg`), PNG (`image/png`), TIFF (`image/tiff`), WebP (`image/webp`)
- Reject files with unsupported MIME types → return `422` with human-readable error
- Reject files exceeding 10 MB → return `413` with human-readable error
- Validate file content matches declared MIME type (magic bytes check)

### EXIF Extraction

- Extract available EXIF metadata from the uploaded image using a Python EXIF library (e.g., `Pillow` or `exifread`)
- Extract fields: camera make/model, date taken, GPS coordinates, exposure settings, image dimensions
- Return EXIF data as a dictionary of key-value pairs; omit fields that are not present
- Handle images without EXIF data gracefully (return empty dictionary)

### AI Metadata Generation

- Call the Azure Content Understanding service (`analyze_image`) to generate:
  - Full-text description (minimum 2 sentences, in German)
  - Keywords / tags (3–15 items, in German)
  - Caption (1–2 sentences, publication-ready, in German)

### Response Model

Define a Pydantic response model:

```
ImageMetadataResponse:
  file_name: str
  file_size: int (bytes)
  mime_type: str
  description: str
  keywords: list[str]
  caption: str
  exif: dict[str, str | float | None]
  processing_time_ms: int
```

### Error Handling

- Return structured error responses for all failure cases
- Log errors with file name (not content), correlation ID, and error details

## Acceptance Criteria

- [x] `POST /api/v1/analyze/image` with a valid JPEG returns 200 with all metadata fields populated
- [x] Description is at least 2 sentences and in German
- [x] Keywords contain between 3 and 15 items
- [x] Caption is 1–2 sentences
- [x] EXIF data is populated when available in the image
- [x] Files exceeding 10 MB return `413` with clear error message
- [x] Unsupported file types return `422` with clear error message
- [x] PNG, TIFF, and WebP formats are accepted and processed successfully
- [x] Response includes `processing_time_ms` as a positive integer
- [x] Endpoint appears in OpenAPI docs at `/docs`

## Testing Requirements

- Unit test: valid JPEG upload returns `ImageMetadataResponse` with all fields
- Unit test: valid PNG upload returns successful response
- Unit test: valid WebP upload returns successful response
- Unit test: file exceeding 10 MB returns 413
- Unit test: unsupported file type (e.g., PDF) returns 422
- Unit test: EXIF data is extracted from image with EXIF
- Unit test: image without EXIF returns empty exif dictionary
- Unit test: processing_time_ms is a positive integer
- Unit test: keywords count is between 3 and 15
- Integration test: end-to-end upload and response (with mocked Azure service)
- Coverage: ≥ 85%
