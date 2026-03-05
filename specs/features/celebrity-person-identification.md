# Feature: Celebrity & Person Identification in Images ("Personenerkennung")

**Parent PRD:** [specs/prd.md](../prd.md)
**Requirements covered:** REQ-17, REQ-18, REQ-19, REQ-20, REQ-21
**Depends on:** [Image Metadata Extraction](image-metadata-extraction.md) (keywords list, analyzer infrastructure)

---

## 1. Overview

When an uploaded image contains a recognizable public figure or celebrity, the system must automatically identify them and include their name(s) in the existing keywords/tags list. This enables editorial staff to search the media archive by person name without manual tagging.

Identification relies on Azure Content Understanding's image analysis capabilities with face blurring disabled (`disable_face_blurring`). The system must only tag persons it identifies with high confidence. Unrecognized faces — including all non-public individuals — must be silently omitted.

!!! warning "Limited Access Blocker"
    The `disable_face_blurring` parameter is an **Azure Limited Access** feature. The Azure subscription must be approved via the [Face Recognition intake form](https://aka.ms/facerecognition) or an Azure support request before this parameter can be used. Until approved, the analyzer operates with face blurring enabled, which significantly limits celebrity identification accuracy. See [Section 7 — Implementation Status](#7-implementation-status) for details.

---

## 2. Functional Requirements

### 2.1 Analyzer Configuration

| ID | Requirement |
|----|-------------|
| CEL-1 | The image analyzer configuration must set `disable_face_blurring = True` so that the AI model can process facial features for person identification. |
| CEL-2 | The analyzer field definitions must include a prompt or field that instructs the model to identify any recognizable public figures or celebrities visible in the image. |
| CEL-3 | The configuration change must apply to the existing `imageMetadataExtractor` custom analyzer — no separate analyzer is required. |

### 2.2 Identification Behavior

| ID | Requirement |
|----|-------------|
| CEL-4 | When one or more recognizable public figures appear in an image, the system must return their names as part of the analysis result. |
| CEL-5 | Identification must be limited to **well-known public figures** (politicians, athletes, entertainers, business leaders, etc.) that the AI model recognizes. The system does not maintain a custom face gallery or database. |
| CEL-6 | If a face in the image cannot be identified as a known public figure, it must be **silently omitted** from the output. No placeholder tags (e.g., "Unbekannte Person", "Unknown person") are permitted. |
| CEL-7 | Only persons identified with **high confidence** should be tagged. Low-confidence or ambiguous matches must be suppressed. |

### 2.3 Output Integration

| ID | Requirement |
|----|-------------|
| CEL-8 | Identified celebrity names must be appended to the **existing keywords/tags list** produced by the image metadata extraction feature. No separate metadata field is introduced. |
| CEL-9 | Person names must be rendered in their **commonly used form** (e.g., "Angela Merkel", "Rafael Nadal") — not translated, abbreviated, or localized. |
| CEL-10 | If the same person appears multiple times in an image, their name must appear only **once** in the keywords list. |
| CEL-11 | Celebrity name tags must coexist with subject-matter keywords without duplication. If the model already generated a keyword matching a person's name, it must not appear twice. |
| CEL-14 | When a recognizable public figure is identified, the generated **description** must reference them by name (e.g., "Angela Merkel spricht auf einer Pressekonferenz" rather than "Eine Frau spricht auf einer Pressekonferenz"). |
| CEL-15 | When a recognizable public figure is identified, the generated **caption** must reference them by name. |

### 2.4 Privacy & Safety

| ID | Requirement |
|----|-------------|
| CEL-12 | The system must **not tag non-public individuals**. Private persons whose faces appear in an image must be excluded from the keywords entirely. |
| CEL-13 | Privacy implications of disabling face blurring must be reviewed with editorial and legal teams before production rollout. |

---

## 3. Acceptance Criteria

- Given an image containing a well-known celebrity (e.g., a press photo of a politician), the celebrity's name appears in the keywords list.
- Given an image containing multiple celebrities, all recognized names appear in the keywords list (each name once).
- Given an image containing only non-public individuals, no person-name keywords are produced.
- Given an image containing both a celebrity and non-public individuals, only the celebrity's name appears — non-public individuals are omitted.
- Given an image with no people, the feature has no effect on the existing keywords (no empty person tags or placeholders).
- The `disable_face_blurring` setting is active in the analyzer configuration used for image analysis.
- Celebrity names appear in their commonly used form (not translated or abbreviated).
- Given an image of a known celebrity, the generated description references the person by name.
- Given an image of a known celebrity, the generated caption references the person by name.
- On the PoC test dataset of celebrity images, ≥ 80 % of known public figures are correctly identified and tagged.
- On the PoC test dataset, zero false positives occur on images of non-public individuals.

---

## 4. Dependencies

| Dependency | Description |
|------------|-------------|
| Image Metadata Extraction | Celebrity names are inserted into the keywords list produced by this feature. The image analysis pipeline, response model, and keyword handling logic are shared. |
| Azure Content Understanding | The `ContentAnalyzerConfig.disable_face_blurring` property must be supported by the SDK version in use (`azure-ai-contentunderstanding`). |
| Azure Limited Access Approval | The `disable_face_blurring` feature requires **Azure Limited Access** registration. Apply via [Face Recognition intake form](https://aka.ms/facerecognition). Without approval, the API rejects `disableFaceBlurring` with `InvalidParameter`. |
| PoC Test Dataset | A set of 5–10 images of well-known public figures must be sourced specifically for validating this feature. These images supplement the existing PoC dataset. |

---

## 5. PoC Validation Plan

### Test Dataset

| Category | Count | Purpose |
|----------|-------|---------|
| Images with a single recognizable celebrity | 3–5 | Validate basic identification accuracy |
| Images with multiple celebrities | 1–2 | Validate multi-person identification |
| Images with non-public individuals only | 2–3 | Validate zero false positives (no person tags produced) |
| Images with a celebrity and non-public individuals together | 1–2 | Validate selective tagging (only celebrity tagged) |

### Success Criteria (per G-6)

- **True positive rate:** ≥ 80 % of known public figures in test images are correctly identified.
- **False positive rate:** 0 % — no non-public individuals tagged in any test image.

---

## 6. Open Questions

- **Q1:** Does the current Azure Content Understanding model reliably identify German public figures (regional politicians, Bundesliga athletes) in addition to globally famous celebrities? — *To be validated during PoC (task 016). Blocked by Limited Access approval — face blurring prevents reliable identification.*
- ~~**Q2:** Is there a confidence score returned alongside person identification that can be used for threshold filtering, or does the model handle confidence internally?~~ — **Resolved:** The `Persons` field returns a plain list of names without confidence scores. The model handles confidence internally — only names it is confident about are returned. Placeholder filtering ("Unknown person", "Mann", etc.) is implemented server-side as an additional safety net.
- ~~**Q3:** Should the description and caption also reference identified persons by name, or only the keywords list?~~ — **Resolved:** Yes. The description and caption must also reference identified persons by name when they are present in the image. The analyzer prompt for Description and Caption fields should be updated to instruct the model to name any recognized public figures.

---

## 7. Implementation Status

*Last updated: 2026-03-05*

### Completed

| Item | Status | Details |
|------|--------|---------|
| Task 014 — Analyzer management script | ✅ Partial | `scripts/update_image_analyzer.py` created. Analyzer deployed to Azure with Persons field and updated Description/Caption prompts. `disable_face_blurring` **cannot be set** until Limited Access is approved. |
| Task 015 — Backend person parsing | ✅ Complete | `_extract_persons()`, `_merge_persons_into_keywords()` implemented in `content_understanding.py`. 19 new unit tests, all 137 tests passing. |
| Task 016 — PoC validation scripts | ✅ Partial | `scripts/validate_celebrity_identification.py` and `scripts/test_images/manifest.json` created. Actual validation blocked pending Limited Access approval. |
| Documentation | ✅ Complete | `azure-content-understanding-usage.md`, `system-design.md`, `rest-api.md` updated. |

### Blocked

| Blocker | Impact | Action Required |
|---------|--------|-----------------|
| **Azure Limited Access** — `disableFaceBlurring` rejected as `InvalidParameter` | Face blurring remains active → model sees pixelated faces → celebrity identification unreliable | Apply via [Face Recognition intake form](https://aka.ms/facerecognition) or open Azure support request. Once approved, re-run `scripts/update_image_analyzer.py` to recreate analyzer with `disable_face_blurring=True`. |

### Current Analyzer State

The `imageMetadataExtractor` analyzer is deployed and `READY` with:
- ✅ `Persons` field (instructs model to identify public figures)
- ✅ Updated Description prompt (names recognized persons)
- ✅ Updated Caption prompt (names recognized persons)
- ✅ Existing Keywords field preserved
- ❌ `disable_face_blurring` NOT set (Limited Access required)

### Known Observations

- With face blurring active, the model describes blurred faces as "Person mit verpixeltem Gesicht" rather than identifying them.
- The model **may** still identify some celebrities from contextual cues (clothing, setting, event branding) even with blurred faces, but this is unreliable.
- **Authentication note**: Analyzer management operations (create/update) require `DefaultAzureCredential` (Entra ID). API key authentication returns HTTP 401 for these operations.
