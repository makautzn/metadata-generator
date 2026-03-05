# 014 — Update Azure Custom Analyzer for Celebrity Identification

## Description

Update the existing `imageMetadataExtractor` custom analyzer in Azure Content Understanding to enable face processing and celebrity identification. This involves two changes to the analyzer definition: (1) setting `disable_face_blurring = true` in the analyzer config so the model can process facial features, and (2) adding a "Persons" field to the analyzer's field schema that instructs the model to identify recognizable public figures in the image.

No separate analyzer is created — the existing `imageMetadataExtractor` is updated in place.

## Feature Reference

- **FRD:** [Celebrity & Person Identification](../features/celebrity-person-identification.md)
- **Requirements covered:** CEL-1, CEL-2, CEL-3, CEL-14, CEL-15

## Dependencies

- **004** — Azure Content Understanding integration service (analyzer infrastructure must exist)

## Technical Requirements

### Analyzer Config Update

- The `imageMetadataExtractor` custom analyzer definition must include `config.disable_face_blurring = true`
- This is set at the **analyzer level** (not per-request) via the `ContentAnalyzerConfig` model when creating/updating the analyzer
- The analyzer must be recreated or updated using the Azure Content Understanding SDK's `begin_create_analyzer` method with `allow_replace = true`

### New Field: Persons

- Add a new field to the analyzer's `fieldSchema` with the following characteristics:
  - **Field name:** `Persons`
  - **Field type:** array of strings
  - **Prompt/description:** Instruct the model to identify any recognizable public figures, celebrities, politicians, athletes, or entertainers visible in the image and return their full commonly used names. If no public figures are recognizable, return an empty list. Do not identify or name private individuals.
- The field prompt must explicitly instruct the model to:
  - Only identify **well-known public figures** (not private individuals)
  - Return names in their **commonly used form** (e.g., "Angela Merkel", not "A. Merkel" or "Frau Merkel")
  - Return an **empty list** if no public figures are identified
  - **Not** return placeholder values like "Unknown person" or "Unbekannte Person"

### Updated Existing Field Prompts: Description & Caption

- Update the **Description** field prompt to instruct the model: "When recognizable public figures or celebrities are visible in the image, refer to them by their commonly used name in the description."
- Update the **Caption** field prompt with the same instruction: "When recognizable public figures or celebrities are visible, name them in the caption."
- These prompt changes ensure that descriptions and captions naturally reference identified persons (e.g., "Angela Merkel spricht auf einer Pressekonferenz" instead of "Eine Frau spricht auf einer Pressekonferenz")

### Analyzer Recreation

- The updated analyzer must be created on API version `2025-11-01` (matching the SDK default)
- The completion model must remain `gpt-4.1-mini`
- The base analyzer must remain `prebuilt-image`
- All existing fields (Description, Caption, Keywords) must be preserved unchanged
- The `Persons` field is added alongside the existing fields

### Validation

- After updating the analyzer, verify it reaches `ready` status
- Submit a test image of a well-known public figure and confirm the `Persons` field is populated in the `AnalyzeResult`
- Submit a test image with no people and confirm the `Persons` field returns an empty list

## Acceptance Criteria

- [ ] ⚠️ **BLOCKED** The `imageMetadataExtractor` analyzer has `config.disable_face_blurring = true` — *`disableFaceBlurring` is an Azure Limited Access feature. API rejects with `InvalidParameter` until subscription is approved via [Face Recognition intake form](https://aka.ms/facerecognition).*
- [x] The analyzer's field schema includes a `Persons` field of array/list type
- [x] The `Persons` field prompt instructs the model to identify only well-known public figures
- [x] Existing fields (Description, Caption, Keywords) remain functional and unchanged
- [x] The analyzer uses API version `2025-11-01` and completion model `gpt-4.1-mini`
- [x] The analyzer reaches `ready` status after update
- [ ] Analyzing an image with a known celebrity returns a non-empty `Persons` field — *Blocked: face blurring prevents reliable identification*
- [ ] Analyzing an image with a known celebrity returns a Description that mentions the person by name — *Blocked: face blurring prevents reliable identification*
- [ ] Analyzing an image with a known celebrity returns a Caption that mentions the person by name — *Blocked: face blurring prevents reliable identification*
- [ ] Analyzing an image with no people returns an empty `Persons` field — *To be verified*

## Implementation Notes

*Added 2026-03-05*

### Deliverables

- **Script:** `scripts/update_image_analyzer.py` — Recreates the analyzer with Persons field, updated prompts, and (when access is granted) `disable_face_blurring=True`.
- **Analyzer status:** Deployed and `READY` in Azure (without `disableFaceBlurring`).

### Findings

1. **Analyzer management requires Entra ID auth** — API key authentication (`AzureKeyCredential`) returns HTTP 401 for `begin_create_analyzer`. Must use `DefaultAzureCredential`.
2. **`disableFaceBlurring` is Limited Access** — The parameter serializes correctly (`camelCase`) but the API rejects it with `InvalidParameter: The parameter DisableFaceBlurring is invalid` unless the subscription has Limited Access approval.
3. **Next step:** Apply for Limited Access, then re-run `python scripts/update_image_analyzer.py`.

## Testing Requirements

- Manual verification: analyzer status is `ready` after recreation ✅
- Manual verification: test image with known celebrity returns populated `Persons` field — *Blocked*
- Manual verification: test image without people returns empty `Persons` field — *Pending*
- Manual verification: Description, Caption, Keywords fields still return correct values ✅
- Document the analyzer creation/update command or script for reproducibility ✅
