# Feature: Audio Metadata Extraction ("Audio Analyse")

**Parent PRD:** [specs/prd.md](../prd.md)
**Requirements covered:** REQ-5, REQ-6, REQ-7, REQ-8

---

## 1. Overview

This feature enables automatic extraction of structured metadata from uploaded audio files. For each audio file the system produces three metadata artifacts: a full-text description, a set of keywords/tags, and a one-sentence summary — all in German.

---

## 2. Functional Requirements

### 2.1 Supported Input

| ID | Requirement |
|----|-------------|
| AUD-1 | The system must accept audio files in MP3, WAV, M4A, and OGG formats. |
| AUD-2 | The system must reject unsupported file types with a clear, user-facing error message. |
| AUD-3 | The system must handle audio files of varying lengths and bitrates without failure. |
| AUD-4 | The system must reject audio files exceeding **15 minutes** in duration with a clear, user-facing error message. |

### 2.2 Metadata Output

| ID | Requirement |
|----|-------------|
| AUD-5 | For each audio file, the system must generate a **full-text description** — a detailed, natural-language summary of the audio content (minimum 2 sentences). |
| AUD-6 | For each audio file, the system must generate a list of **keywords / tags** — relevant terms suitable for search indexing and categorization (minimum 3, maximum 15 keywords). |
| AUD-7 | For each audio file, the system must generate a **one-sentence summary** (Kurz-Zusammenfassung). |
| AUD-8 | All generated metadata must be in **German**. |

### 2.3 Volume & Performance

| ID | Requirement |
|----|-------------|
| AUD-9 | PoC phase: the feature must successfully process **at least 2 audio files**. |
| AUD-10 | Audio processing time is expected to correlate with file duration; the system should provide progress feedback for longer files. |

---

## 3. Acceptance Criteria

- Given a valid audio file upload, the system returns a description, keywords, and one-sentence summary.
- Given an unsupported file format, the system displays an appropriate error and does not attempt processing.
- At least 80 % of generated metadata for the PoC dataset is rated "usable" or "good" by editorial reviewers.
- All output text is in German.

---

## 4. Resolved Questions

- **What is the maximum acceptable audio file duration or file size?** — Maximum **15 minutes** per audio file. *(Originally 10 minutes; extended during E2E testing to accommodate real-world editorial audio.)*
- **Should the system also produce a transcript in addition to the summary metadata?** — No, transcript output is not required.
- **Is there a target production volume for audio files per month?** — No, there is no defined production volume target for audio files at this time.

---

## 5. E2E Testing Findings

The following issues were identified and resolved during end-to-end testing (2026-02-16):

| Finding | Resolution |
|---------|-----------|
| Azure SDK (`azure-ai-contentunderstanding`) uses API version `2025-11-01` by default; custom analyzers created on `2024-12-01-preview` were invisible to the SDK → `ModelNotFound` error. | Recreated custom analyzers (`audioMetadataExtractor`) on API version `2025-11-01` with `models.completion: gpt-4.1-mini`. |
| Analyzer IDs containing hyphens (e.g. `audio-metadata-extractor`) are rejected on `2025-11-01`. | Switched to camelCase IDs: `audioMetadataExtractor`. |
| Keywords returned as raw `ContentField` objects (e.g. `{'type': 'string', 'valueString': 'Tennis'}`) instead of plain strings. | Fixed keyword extraction to read `k.value` from each `ContentField` item. |
| One-sentence summary (Kurz-Zusammenfassung) was a full paragraph. | Updated analyzer `Summary` field prompt to enforce single sentence (max 30 words). Added backend `_truncate_to_first_sentence()` safeguard. |
| Audio tile displayed summary above description; users expected long description on top, short summary below. | Swapped order in `AudioTile` component: description first, summary second. |
| `min_length=3` on `keywords` field was too strict — Azure sometimes returns fewer. | Relaxed `min_length` from 3 to 1 in both `ImageAnalysisResult` and `AudioAnalysisResult`. |
| `aiohttp` not listed as a dependency but required at runtime by the Azure SDK. | Added `aiohttp` to `pyproject.toml` dependencies. |
