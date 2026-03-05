# 016 — PoC Celebrity Test Dataset & Validation

## Description

Source a set of test images containing known celebrities and non-public individuals, then validate the end-to-end celebrity identification pipeline against the acceptance criteria defined in the FRD and PRD goal G-6. This task produces a documented validation report with pass/fail results per test image.

## Feature Reference

- **FRD:** [Celebrity & Person Identification](../features/celebrity-person-identification.md) — Section 5 (PoC Validation Plan)
- **PRD Goal:** G-6 (≥ 80% true positive, 0% false positive)
- **Requirements covered:** CEL-4, CEL-5, CEL-6, CEL-7, CEL-12

## Dependencies

- **014** — Azure analyzer updated with `Persons` field and `disable_face_blurring`
- **015** — Backend parsing merges person names into keywords

## Technical Requirements

### Test Dataset Composition

Source test images covering the following categories (per FRD Section 5):

| Category | Count | Purpose |
|----------|-------|---------|
| Single recognizable celebrity | 3–5 | Validate basic identification accuracy |
| Multiple celebrities in one image | 1–2 | Validate multi-person identification |
| Non-public individuals only | 2–3 | Validate zero false positives |
| Celebrity mixed with non-public individuals | 1–2 | Validate selective tagging |

- Images must be in supported formats (JPEG, PNG, WebP)
- Images must be ≤ 10 MB
- Use publicly available press/editorial images with appropriate licensing for testing purposes
- Include a mix of internationally famous and German public figures (to test Q1 from FRD)

### Test Execution

- Upload each test image through the running application (either via the web UI or directly via `POST /api/v1/analyze/image`)
- Record the returned keywords list for each image
- Identify which keywords are person names vs. subject-matter tags

### Validation Criteria

- **True positive rate:** Count of correctly identified known public figures ÷ total known public figures in test images. Must be ≥ 80%.
- **False positive rate:** Count of non-public individuals incorrectly tagged ÷ total images with non-public individuals. Must be 0%.
- **Name quality:** Person names must be in their commonly used form (not abbreviated, not translated)
- **No placeholders:** No "Unknown person" / "Unbekannte Person" entries in any result
- **Deduplication:** No duplicate person names in any keywords list
- **Coexistence:** Person names coexist with subject-matter keywords without corruption
- **Description references:** For images with identified celebrities, the description must mention the person by name
- **Caption references:** For images with identified celebrities, the caption must mention the person by name

### Documentation

- Record results in the FRD file under a new "E2E Testing Findings" section (consistent with existing FRD conventions)
- Include a summary table: image file name, expected persons, actual persons returned, pass/fail
- Document any issues discovered and their resolutions
- Note the accuracy rates achieved

## Acceptance Criteria

- [ ] Test dataset of 8–12 images sourced covering all four categories — *Blocked: needs Limited Access approval for reliable testing*
- [ ] All test images processed successfully through the system
- [ ] True positive identification rate ≥ 80%
- [ ] False positive rate = 0% (no non-public individuals tagged)
- [ ] No placeholder tags in any result
- [ ] Person names are in commonly used form
- [ ] Descriptions reference identified celebrities by name
- [ ] Captions reference identified celebrities by name
- [ ] Validation results documented in the FRD with a summary table
- [ ] Any issues discovered are documented with resolutions
- [ ] FRD open questions Q1 and Q2 answered based on test results

## Implementation Notes

*Updated 2026-03-05*

### Deliverables Created

- `scripts/validate_celebrity_identification.py` — Automated validation script that reads `test_images/manifest.json`, uploads images to the API, validates TP/FP rates, checks description/caption person references, and writes a JSON report.
- `scripts/test_images/manifest.json` — Template manifest with 5 example categories. Needs real test image filenames inserted.

### Current Status: Blocked

Validation cannot produce meaningful results until the **Azure Limited Access** approval is granted and `disable_face_blurring=True` is set on the analyzer. With face blurring active:
- The model sees pixelated faces and cannot reliably identify celebrities.
- Testing would produce artificially low TP rates that do not reflect the feature's actual capability.

### Next Steps

1. Obtain Limited Access approval for `disableFaceBlurring`
2. Re-run `scripts/update_image_analyzer.py` to update analyzer
3. Source 8–12 test images and update `manifest.json`
4. Run `python scripts/validate_celebrity_identification.py` against running API
5. Document results in FRD Section 7

## Testing Requirements

- E2E test: each test image uploaded and response recorded
- E2E test: accuracy metrics calculated and compared against thresholds
- E2E test: regression check — existing PoC images (non-celebrity) still produce correct metadata
- Documentation: validation report added to FRD
