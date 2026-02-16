# 012 — Frontend Copy-to-Clipboard & Export

## Description

Implement copy-to-clipboard functionality for individual metadata fields and CSV/JSON export for all processed results. These features enable editorial staff to quickly transfer metadata to other systems. Covers requirements WEB-13 and WEB-14.

## Dependencies

- **011** — Frontend metadata display tiles (tiles must exist to add copy buttons)

## Technical Requirements

### Copy-to-Clipboard

- Add a copy button (icon button) next to each copiable metadata field:
  - Description (copies full text)
  - Keywords (copies as comma-separated string)
  - Caption / Summary (copies full text)
- Use the Clipboard API (`navigator.clipboard.writeText()`)
- Show brief visual feedback on copy success (e.g., tooltip "Kopiert!" or icon change for 2 seconds)
- Handle clipboard API unavailability gracefully (e.g., show error or fall back to `document.execCommand`)

### JSON Export

- Add a "JSON herunterladen" button in the results area (visible when ≥1 result exists)
- Export all processed results as a JSON file
- JSON structure should match the batch API response schema
- File name: `metadata-export-{timestamp}.json`
- Trigger browser download via `Blob` + `URL.createObjectURL`

### CSV Export

- Add a "CSV herunterladen" button alongside the JSON button
- Export all processed results as a CSV file with the following columns:
  - `file_name`, `file_type`, `description`, `keywords` (semicolon-separated within the cell), `caption_or_summary`, `processing_time_ms`
  - For images: include `exif_camera`, `exif_date`, `exif_gps` as additional columns
- Handle special characters (commas, quotes, newlines) in CSV values via proper escaping
- File name: `metadata-export-{timestamp}.csv`
- Use UTF-8 encoding with BOM for Excel compatibility

### UI Placement

- Copy buttons appear inline within each tile, next to the respective field
- Export buttons appear above or below the tile grid as a button group
- Export buttons are disabled when no results are available

## Acceptance Criteria

- [x] Clicking copy on description copies the full text to clipboard
- [x] Clicking copy on keywords copies them as a comma-separated string
- [x] Clicking copy on caption/summary copies the full text
- [x] Copy success shows brief "Kopiert!" feedback
- [x] "JSON herunterladen" downloads a valid JSON file with all results
- [x] "CSV herunterladen" downloads a valid CSV file with all results
- [x] CSV is properly escaped and UTF-8 encoded with BOM
- [x] Export buttons are disabled when no results exist
- [x] Export buttons are enabled when results are available
- [x] Downloaded file names include a timestamp

## Testing Requirements

- Unit test: copy button calls `navigator.clipboard.writeText` with correct value
- Unit test: copy button shows success feedback after click
- Unit test: keywords are formatted as comma-separated string for clipboard
- Unit test: JSON export generates valid JSON matching the expected schema
- Unit test: CSV export generates valid CSV with correct headers and escaping
- Unit test: CSV includes BOM prefix for UTF-8
- Unit test: export buttons are disabled when results array is empty
- Unit test: export buttons are enabled when results exist
- Unit test: file download is triggered with correct file name pattern
- Unit test: copy fallback works when Clipboard API is unavailable
- Coverage: ≥ 85%
