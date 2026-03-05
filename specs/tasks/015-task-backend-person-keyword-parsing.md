# 015 — Backend Keyword Parsing for Person Identification

## Description

Update the backend service's image result parsing logic to extract identified person names from the new `Persons` field returned by the Azure analyzer and merge them into the existing keywords list. No new response model fields are introduced — celebrity names appear as entries in the existing `keywords: list[str]` field, ensuring a single unified tagging vocabulary.

## Feature Reference

- **FRD:** [Celebrity & Person Identification](../features/celebrity-person-identification.md)
- **Requirements covered:** CEL-4, CEL-5, CEL-6, CEL-7, CEL-8, CEL-9, CEL-10, CEL-11, CEL-12

## Dependencies

- **014** — Azure analyzer updated with `Persons` field and `disable_face_blurring`
- **004** — Azure Content Understanding integration service
- **005** — Image metadata extraction API

## Technical Requirements

### Person Name Extraction

- In the `_parse_image_result()` method (or equivalent), extract the `Persons` field from the `AnalyzeResult.contents[0].fields` dictionary
- The `Persons` field is an array-type `ContentField` — each element's `.value` is a string containing a person's name
- Use the same extraction pattern as keywords (`getattr(item, "value", item)`)
- If the `Persons` field is absent, empty, or `None`, treat it as an empty list (no error)

### Filtering

- Discard any entry that is a placeholder or generic label (e.g., contains "unknown", "unbekannt", "person", "Mann", "Frau" as the entire value)
- Discard entries that contain markdown artifact characters (`[]`, `()`, `#`, `|`, `/`) — same filter as existing keywords
- Discard empty strings and whitespace-only entries
- Trim leading/trailing whitespace from names

### Deduplication and Merging

- After extracting person names, merge them into the keywords list that was already extracted from the `Keywords` field
- Perform case-insensitive deduplication: if a person name already appears in the keywords list (exact or case-insensitive match), do not add it again
- Person name entries should be appended after subject-matter keywords (append to end of list)
- The combined keywords list must still respect the maximum of 15 entries; if adding person names would exceed the limit, prioritize subject-matter keywords and add as many person names as fit

### No Response Model Changes

- The `ImageMetadataResponse` and `ImageAnalysisResult` models remain unchanged
- Celebrity names are part of `keywords: list[str]` — no new field is added
- The `AudioAnalysisResult` and audio parsing logic are not affected

## Acceptance Criteria

- [x] When the Azure analyzer returns a `Persons` field with celebrity names, those names appear in the `keywords` list of the `ImageMetadataResponse`
- [x] When the `Persons` field is empty or absent, the keywords list is unchanged from current behavior
- [x] Person names are deduplicated against existing keywords (case-insensitive)
- [x] Placeholder values (e.g., "Unknown person") are filtered out and do not appear in keywords
- [x] Person names are rendered in their commonly used form (not abbreviated or translated)
- [x] The combined keywords list does not exceed 15 entries
- [x] Markdown artifact characters in person names are filtered out
- [x] The `ImageMetadataResponse` schema is unchanged (no new fields)
- [x] Audio analysis is completely unaffected
- [x] All existing image metadata extraction tests continue to pass

## Testing Requirements

All tests implemented and passing (137 total, 19 new for person identification):

- [x] Unit test: `_parse_image_result()` with a `Persons` field containing `["Angela Merkel"]` returns "Angela Merkel" in the keywords list
- [x] Unit test: `_parse_image_result()` with a `Persons` field containing multiple names returns all names in keywords
- [x] Unit test: `_parse_image_result()` with an empty `Persons` field returns keywords unchanged
- [x] Unit test: `_parse_image_result()` with a missing `Persons` field returns keywords unchanged (no error)
- [x] Unit test: duplicate person name already in keywords list is not added twice
- [x] Unit test: case-insensitive deduplication works (e.g., "angela merkel" in keywords, "Angela Merkel" in Persons → no duplicate)
- [x] Unit test: placeholder values like "Unknown person" and "Unbekannte Person" are filtered out
- [x] Unit test: person names with markdown artifacts are filtered out
- [x] Unit test: combined keywords list does not exceed 15 entries when person names are added
- [x] Unit test: person names are appended after subject-matter keywords
- [x] Unit test: whitespace-only and empty person name entries are discarded
- [x] Regression test: all existing image endpoint tests pass without modification
- [x] Regression test: all existing audio endpoint tests pass without modification
- [x] Integration test: `POST /api/v1/analyze/image` with mocked Azure response containing `Persons` field returns celebrity names in keywords
- Coverage: ≥ 85%

## Implementation Notes

*Completed 2026-03-05*

### Files Modified

- `MetadataGenerator.Api/app/services/content_understanding.py` — Added `_PERSON_PLACEHOLDER_PATTERNS` (frozenset), `_extract_persons()`, `_merge_persons_into_keywords()`, updated `_parse_image_result()`
- `MetadataGenerator.Api/tests/test_content_understanding_service.py` — Added `TestPersonExtraction` (11 tests) and `TestPersonExtractionUnit` (8 tests)

### Key Design Decisions

- Person names are extracted from the `Persons` `ContentField` using the same pattern as keywords (`getattr(item, "value", item)`)
- Placeholder filtering uses a frozen set of lowercase patterns matched against the full name value
- Merging appends after subject keywords with case-insensitive dedup, capped at 15 total
