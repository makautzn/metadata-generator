# Feature: Image Metadata Extraction ("Bildverschlagwortung")

**Parent PRD:** [specs/prd.md](../prd.md)
**Requirements covered:** REQ-1, REQ-2, REQ-3, REQ-4

---

## 1. Overview

This feature enables automatic extraction of structured metadata from uploaded images. For each image the system produces three metadata artifacts: a full-text description, a set of keywords/tags, and a publication-ready caption — all in German.

---

## 2. Functional Requirements

### 2.1 Supported Input

| ID | Requirement |
|----|-------------|
| IMG-1 | The system must accept images in JPEG, PNG, TIFF, and WebP formats. |
| IMG-2 | The system must reject unsupported file types with a clear, user-facing error message. |
| IMG-3 | The system must handle images of varying resolutions and aspect ratios without failure. |
| IMG-4 | The system must reject images exceeding **10 MB** in file size with a clear, user-facing error message. |

### 2.2 Metadata Output

| ID | Requirement |
|----|-------------|
| IMG-5 | For each image, the system must generate a **full-text description** — a detailed, natural-language depiction of the image content (minimum 2 sentences). |
| IMG-6 | For each image, the system must generate a list of **keywords / tags** — relevant terms suitable for search indexing and categorization (minimum 3, maximum 15 keywords). |
| IMG-7 | For each image, the system must generate a **caption** — a concise, publication-ready subtitle (maximum 1–2 sentences). |
| IMG-8 | For each image, the system must extract and display available **EXIF metadata** (e.g., geolocation, camera model, date taken, exposure settings). |
| IMG-9 | All AI-generated metadata must be in **German**. |

### 2.3 Volume & Performance

| ID | Requirement |
|----|-------------|
| IMG-10 | PoC phase: the feature must successfully process a dataset of **10–20 images**. |
| IMG-11 | Production phase: the feature must support processing of **≥ 5 000 images per month**. |
| IMG-12 | Individual image processing should complete within a reasonable time frame that does not disrupt the user's workflow (exact threshold to be validated during PoC). |

---

## 3. Acceptance Criteria

- Given a valid image upload, the system returns a description, keywords, caption, and EXIF data within the expected timeframe.
- Given an image exceeding 10 MB, the system rejects the upload with a clear error message.
- Given an unsupported file format, the system displays an appropriate error and does not attempt processing.
- At least 80 % of generated metadata for the PoC dataset is rated "usable" or "good" by editorial reviewers.
- All output text is in German.

---

## 4. Resolved Questions

- **What is the maximum acceptable file size per image?** — Maximum **10 MB** per image.
- **Should EXIF data embedded in the image be surfaced alongside AI-generated metadata?** — Yes, EXIF data (e.g., geolocation, camera model, date taken) should be extracted and displayed.
- **Are there specific editorial style guidelines the caption should follow?** — No, no specific style guidelines apply.
