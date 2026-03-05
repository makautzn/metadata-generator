# 009 — Frontend Multi-File Upload Component

## Description

Implement the file upload component that allows users to select or drag-and-drop multiple image and audio files. This component handles client-side validation (file type, file count), displays the list of selected files, and triggers the batch upload to the backend API. Covers requirements WEB-1 through WEB-5.

## Dependencies

- **002** — Frontend web app scaffolding
- **008** — Frontend design system

## Technical Requirements

### Upload Component

- Create a `FileUpload` component in `components/`
- Support two input methods:
  1. **Click to browse** — Opens native file picker with `accept` attribute filtering to supported types
  2. **Drag and drop** — Drop zone area with visual feedback on drag-over
- Accepted file types: JPEG, PNG, TIFF, WebP, MP3, WAV, M4A, OGG
- Maximum 20 files per upload action

### Client-Side Validation

- Validate file type against the accepted list — show inline error for rejected files
- Validate total file count ≤ 20 — show error message if exceeded
- Validate individual image file size ≤ 10 MB — show inline error
- Display validation errors immediately upon selection, before any upload begins

### Selected Files List

- After file selection, display a list/preview of selected files before upload
- Each entry shows: file name, file size (human-readable, e.g., "2.4 MB"), file type icon (image/audio), validation status
- Allow users to remove individual files from the selection
- Provide a "Clear all" action

### Upload Trigger

- A prominent "Analyze" / "Verarbeiten" button triggers the batch upload
- Button is disabled until at least 1 valid file is selected
- On click, send all valid files to `POST /api/v1/analyze/batch` via the API client
- Button shows loading state during upload

### Drop Zone UX

- Visual drop zone with dashed border and instructional text (e.g., "Dateien hierher ziehen oder klicken zum Auswählen")
- Highlight state on drag-over (border color change, background tint)
- Return to normal state on drag-leave or drop

## Acceptance Criteria

- [x] User can click to open file picker and select multiple files
- [x] User can drag and drop files onto the drop zone
- [x] Drop zone shows visual highlight during drag-over
- [x] Selected files appear in a list with name, size, and type
- [x] Selecting > 20 files triggers a clear error message
- [x] Invalid file types are immediately flagged with an error
- [x] Image files > 10 MB are flagged with a size error
- [x] Users can remove individual files from the selection
- [x] "Analyze" button is disabled when no valid files are selected
- [x] "Analyze" button triggers API call with all valid files
- [x] Upload instructional text is in German

## Implementation Notes

### Per-File Sequential Upload (Refactored 2026-03-05)

The upload component was refactored from a single batch request (`POST /analyze/batch`) to **per-file sequential uploads** to avoid proxy timeouts when audio files take 10–20+ minutes to process:

- **Images**: Uploaded one at a time via `POST /api/v1/analyze/image`. Each takes ~30 s.
- **Audio files**: Submitted via `POST /api/v1/analyze/audio/submit` (returns `job_id`, HTTP 202), then polled via `GET /api/v1/analyze/audio/status/{job_id}` every 5 seconds until complete.
- Results are displayed **progressively** as each file completes via the `onFileResult` callback.
- The batch endpoint remains available for direct API consumers.

## Testing Requirements

- Unit test: component renders drop zone with instructional text
- Unit test: file selection updates the file list display
- Unit test: selecting > 20 files shows validation error
- Unit test: unsupported file type shows inline error
- Unit test: oversized image file shows inline error
- Unit test: remove button removes a file from the list
- Unit test: "Clear all" removes all files
- Unit test: "Analyze" button is disabled when file list is empty
- Unit test: "Analyze" button is enabled when valid files are selected
- Unit test: drag-over triggers highlight state
- Integration test: clicking "Analyze" calls the API client with selected files
- Coverage: ≥ 85%
