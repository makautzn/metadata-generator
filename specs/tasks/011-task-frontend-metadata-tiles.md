# 011 — Frontend Metadata Display Tiles

## Description

Implement the content of image and audio metadata tiles, displaying all extracted metadata fields within the tile cards. Image tiles show a thumbnail, description, keywords, caption, and EXIF data. Audio tiles show an audio icon, description, keywords, and one-sentence summary. Covers requirements WEB-10 through WEB-12.

## Dependencies

- **002** — Frontend web app scaffolding
- **008** — Frontend design system
- **010** — Frontend processing feedback & tile grid

## Technical Requirements

### Image Metadata Tile

Create an `ImageTile` component that renders inside the Card from the tile grid:

- **Thumbnail**: Display a scaled-down preview of the uploaded image (use object URL or base64)
- **Description**: Full-text description in a readable paragraph block
- **Keywords**: Rendered as **tag chips/badges** using the Badge component from the design system
- **Caption**: Displayed as a styled subtitle/quote block below the description
- **EXIF section**: Collapsible/expandable section showing EXIF key-value pairs (camera model, date, GPS, dimensions, etc.). Hidden by default to keep tiles compact.
- **Processing time**: Shown as a subtle footnote (e.g., "Verarbeitet in 1.2s")

### Audio Metadata Tile

Create an `AudioTile` component:

- **Audio icon**: Display a recognizable audio/waveform icon or placeholder graphic (no actual audio player needed for PoC)
- **Description**: Full-text description in a readable paragraph block
- **Keywords**: Rendered as **tag chips/badges**
- **Summary**: One-sentence summary displayed prominently (e.g., bold or highlighted)
- **Duration**: Display audio duration (e.g., "Dauer: 3:42")
- **Processing time**: Subtle footnote

### Shared Behavior

- Both tile types use the same Card wrapper and consistent internal spacing
- Long descriptions should be truncatable with a "Mehr anzeigen" / "Weniger anzeigen" toggle
- Keywords should wrap naturally across multiple lines in the badge/chip layout
- All text labels should be in German

### TypeScript Types

Define shared types in `lib/types.ts`:
- `ImageMetadata` matching the backend `ImageMetadataResponse` schema
- `AudioMetadata` matching the backend `AudioMetadataResponse` schema
- `FileResult` union type covering both

## Acceptance Criteria

- [x] Image tile shows thumbnail, description, keywords (as chips), caption, and EXIF
- [x] Audio tile shows icon, description, keywords (as chips), summary, and duration
- [x] Keywords render as visual tag chips/badges
- [x] EXIF section is collapsible and hidden by default
- [x] Long descriptions can be expanded/collapsed
- [x] Processing time is displayed on each tile
- [x] All UI labels are in German
- [x] Tiles handle missing optional fields gracefully (e.g., no EXIF → section hidden)

## Testing Requirements

- Unit test: ImageTile renders all metadata fields (description, keywords, caption)
- Unit test: ImageTile renders thumbnail image
- Unit test: ImageTile renders EXIF data when present
- Unit test: ImageTile hides EXIF section when EXIF is empty
- Unit test: AudioTile renders all metadata fields (description, keywords, summary)
- Unit test: AudioTile renders duration in human-readable format
- Unit test: keywords render as Badge/Chip components
- Unit test: long description expand/collapse toggle works
- Unit test: tile handles missing optional fields without errors
- Snapshot test: ImageTile and AudioTile match expected structure
- Coverage: ≥ 85%
