# Feature: PoC Web Application

**Parent PRD:** [specs/prd.md](../prd.md)
**Requirements covered:** REQ-9, REQ-10, REQ-11, REQ-12, REQ-13

---

## 1. Overview

A single-page web application that serves as the user-facing front end for the PoC. It allows editorial testers to upload multiple image and audio files, triggers metadata extraction, and presents the results in a visual tile layout. The look and feel is inspired by *DIE RHEINPFALZ* (clean, modern, editorial aesthetic).

---

## 2. Functional Requirements

### 2.1 File Upload

| ID | Requirement |
|----|-------------|
| WEB-1 | The application must provide a **multi-file upload** control that supports selecting or drag-and-dropping multiple files in a single action. |
| WEB-2 | Accepted file types must match the union of supported image formats (JPEG, PNG, TIFF, WebP) and audio formats (MP3, WAV, M4A, OGG). |
| WEB-3 | The upload control must display a clear indication of which files have been selected before the user triggers processing. |
| WEB-4 | The application must validate file types on the client side and inform the user immediately if an unsupported file is selected. |
| WEB-5 | The application must enforce a **maximum of 20 files** per upload action. If more are selected, the user must be informed and the excess files rejected. |

### 2.2 Processing & Feedback

| ID | Requirement |
|----|-------------|
| WEB-6 | After upload, the application must show **per-file progress indicators** (e.g., spinner, progress bar, or status label) while metadata extraction is in progress. |
| WEB-7 | If processing fails for a specific file, the corresponding tile must display an **error state** with a human-readable message. |

### 2.3 Tile View — Metadata Display

| ID | Requirement |
|----|-------------|
| WEB-8 | Each processed file must be displayed as a **tile** in a responsive grid layout. |
| WEB-9 | Tiles must be ordered by **upload order** (the sequence in which the user selected/dropped the files). |
| WEB-10 | **Image tiles** must show: a thumbnail of the image, plus the generated description, keywords, and caption. |
| WEB-11 | **Audio tiles** must show: an audio icon or waveform placeholder, plus the generated description, keywords, and one-sentence summary. |
| WEB-12 | Keywords must be displayed as **tag chips/badges** for easy visual scanning. |
| WEB-13 | Users must be able to **copy** individual metadata fields (description, keywords, caption/summary) to the clipboard. |
| WEB-14 | Users must be able to **export** all processed results as **CSV** or **JSON** via download buttons. |

### 2.4 Design & Layout

| ID | Requirement |
|----|-------------|
| WEB-15 | The application must be a **single page** — no multi-page navigation or routing required. |
| WEB-16 | The visual design must follow the **editorial, clean aesthetic** of *DIE RHEINPFALZ* (Aktuelle Nachrichten aus der Pfalz) — neutral color palette, clear typography, structured layout. |
| WEB-17 | The layout must be **responsive** and usable on desktop screens (mobile optimization is not required for the PoC). |

---

## 3. Acceptance Criteria

- A user can select and upload up to 20 files (mix of images and audio) in a single action.
- Selecting more than 20 files triggers a clear validation message.
- While files are processing, the user sees individual progress states per file.
- After processing completes, each file appears as a tile in upload order showing all extracted metadata fields.
- The visual design is perceived as "clean and professional" by editorial stakeholders (qualitative feedback).
- Copy-to-clipboard works for each metadata field.
- The user can download all results as CSV or JSON.

---

## 4. Resolved Questions

- **Should there be a maximum number of files that can be uploaded at once?** — Yes, maximum **20 files** per upload.
- **Is there a preference for the order of tiles?** — Tiles are displayed in **upload order**.
- **Should processed results be exportable?** — Yes, results must be exportable as **CSV** and **JSON**.
- **Should there be a "re-process" or "retry" action per file?** — No, not required for the PoC.
