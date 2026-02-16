# 010 — Frontend Processing Feedback & Tile Grid

## Description

Implement per-file progress indicators during metadata extraction and the responsive tile grid layout that displays results. While the backend processes files, each file should show its processing state (pending, processing, complete, error). Completed files transition into metadata tiles in the grid. Covers requirements WEB-6 through WEB-9.

## Dependencies

- **002** — Frontend web app scaffolding
- **008** — Frontend design system
- **009** — Frontend multi-file upload component

## Technical Requirements

### Processing State Management

- Define a state model for each file's lifecycle:
  - `pending` — file submitted, waiting to be processed
  - `processing` — currently being analyzed
  - `success` — metadata extraction complete
  - `error` — processing failed
- Use React state (or Zustand/Jotai) to track all files and their states
- Update state as results arrive from the batch API response

### Progress Indicators

- Each file in the processing queue shows:
  - File name and type icon
  - Status: spinner for `processing`, checkmark for `success`, error icon for `error`
  - For errors: human-readable error message below the file entry
- Show an overall progress summary: "X of Y files processed"

### Tile Grid Layout

- Completed files render as cards/tiles in a responsive CSS Grid
- Grid auto-fills columns with a minimum tile width (320px recommended)
- Tiles appear in **upload order** as defined by `file_index` from the API response
- Grid reflows responsively for different desktop viewport widths
- Tiles use the Card component from the design system

### Tile Structure

Each tile contains:
- **Header area**: File name, file type badge (Image / Audio), processing time
- **Content area**: Placeholder for metadata fields (populated by tasks 011)
- **Status indicator**: Success or error state

### Error Tiles

- Files that failed processing render as tiles in an error state
- Error tiles show the file name and error message
- Error tiles are visually distinct (e.g., red-tinted border or background)

## Acceptance Criteria

- [x] After triggering upload, each file shows a progress indicator
- [x] Spinners appear for files being processed
- [x] Completed files transition to tiles in the grid
- [x] Failed files show error tiles with human-readable messages
- [x] Overall progress summary ("X of Y processed") is visible
- [x] Tiles appear in upload order
- [x] Grid layout is responsive on desktop viewports
- [x] Grid reflows correctly when viewport is resized

## Testing Requirements

- Unit test: file state transitions correctly (pending → processing → success)
- Unit test: file state transitions to error on failure
- Unit test: progress indicator shows spinner for processing state
- Unit test: progress indicator shows checkmark for success state
- Unit test: error tile displays error message
- Unit test: overall progress counter updates correctly
- Unit test: tiles render in upload order by file_index
- Unit test: grid container renders with correct CSS grid properties
- Integration test: state updates correctly when API response is received
- Coverage: ≥ 85%
