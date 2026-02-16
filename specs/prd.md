# 📝 Product Requirements Document (PRD)

## Metadata Generator — PoC & Production Vision

---

## 1. Purpose

Media organizations handle large volumes of images and audio files daily. Manually tagging, describing, and cataloguing these assets is time-consuming, inconsistent, and does not scale. This product automates the extraction of structured metadata (descriptions, keywords, captions, summaries) from image and audio files using AI-powered content understanding.

The **Proof of Concept (PoC)** validates the feasibility and quality of automated metadata extraction on a small, representative dataset. The **Production** phase scales the solution to handle real editorial workloads and integrates into existing publishing workflows.

**Primary users:** Editorial staff, media librarians, and content managers at a regional news publisher (modeled on *DIE RHEINPFALZ*).

---

## 2. Scope

### In Scope

- **Image Metadata Extraction** — Automatically generate a full-text description, a set of keywords/tags, and a caption for uploaded images.
- **Audio Metadata Extraction** — Automatically generate a full-text description, a set of keywords/tags, and a one-sentence summary for uploaded audio files.
- **PoC Web Application** — A simple, modern, single-page website that allows multi-file upload and displays extracted metadata in a tile view.
- **PoC Design Direction** — Visual design inspired by *DIE RHEINPFALZ* (Aktuelle Nachrichten aus der Pfalz).
- **Production Webhook Integration** — A webhook endpoint that external systems can call to trigger metadata extraction and receive results.

### Out of Scope

- Video file analysis.
- User authentication / role-based access control (PoC phase).
- Long-term asset storage or Digital Asset Management (DAM) capabilities.
- Editorial workflow management beyond metadata extraction.
- Bulk re-processing of historical archives (may be considered post-production).
- Multi-language output beyond German (initial target language).

---

## 3. Goals & Success Criteria

| # | Goal | Success Metric |
|---|------|----------------|
| G-1 | Validate that AI-generated image metadata meets editorial quality standards | ≥ 80 % of generated descriptions, keywords, and captions rated "usable" or "good" by editorial reviewers on the PoC dataset (10–20 images) |
| G-2 | Validate that AI-generated audio metadata meets editorial quality standards | ≥ 80 % of generated descriptions, keywords, and summaries rated "usable" or "good" by editorial reviewers on the PoC dataset (2 audio files) |
| G-3 | Demonstrate a usable self-service upload experience | Editorial testers can upload files and view results without training or documentation |
| G-4 | Confirm production-scale feasibility | Architecture review confirms the solution can handle ≥ 5 000 images/month with acceptable latency and cost |
| G-5 | Enable system integration via webhook | External systems can trigger extraction and receive structured metadata via a documented webhook contract |

---

## 4. High-Level Requirements

### Image Metadata Extraction ("Bildverschlagwortung")

- **[REQ-1]** The system must accept common image formats (JPEG, PNG, TIFF, WebP) for processing.
- **[REQ-2]** For each uploaded image the system must generate:
  - a **full-text description** (detailed, natural-language depiction of the image content),
  - a set of **keywords / tags** (relevant terms for search and categorization),
  - a **caption** (a concise, publication-ready image subtitle).
- **[REQ-3]** Generated metadata must be in **German**.
- **[REQ-4]** PoC must support processing of **10–20 images**; Production must support **≥ 5 000 images per month**.

### Audio Metadata Extraction ("Audio Analyse")

- **[REQ-5]** The system must accept common audio formats (MP3, WAV, M4A, OGG) for processing.
- **[REQ-6]** For each uploaded audio file the system must generate:
  - a **full-text description** (detailed, natural-language summary of the audio content),
  - a set of **keywords / tags**,
  - a **one-sentence summary**.
- **[REQ-7]** Generated metadata must be in **German**.
- **[REQ-8]** PoC must support processing of **at least 2 audio files**.

### PoC Web Application

- **[REQ-9]** The application must be a **single-page web application** with a clean, modern design inspired by *DIE RHEINPFALZ*.
- **[REQ-10]** Users must be able to **upload multiple files at once** (images and/or audio).
- **[REQ-11]** Extracted metadata must be displayed in a **tile view**, with each tile representing one uploaded file and its associated metadata.
- **[REQ-12]** The application must provide clear **progress/status feedback** during file processing.
- **[REQ-13]** The application must use **Azure Content Understanding** as the AI backend for metadata extraction.

### Production Integration

- **[REQ-14]** The system must expose a **webhook endpoint** that accepts file references, triggers metadata extraction, and returns structured metadata results.
- **[REQ-15]** The webhook response must follow a **consistent, documented schema** so that consuming systems can reliably parse the output.
- **[REQ-16]** The system must handle **≥ 5 000 images per month** in production with acceptable performance (response time target to be defined during PoC evaluation).

---

## 5. User Stories

### Image Metadata Extraction

```gherkin
As an editorial staff member,
I want to upload one or more images and automatically receive a description, keywords, and a caption for each,
so that I can quickly catalogue and publish images without writing metadata manually.
```

```gherkin
As a media librarian,
I want consistent, high-quality keywords generated for every image,
so that editorial colleagues can find images efficiently through search.
```

### Audio Metadata Extraction

```gherkin
As an editorial staff member,
I want to upload an audio file and receive a description, keywords, and a one-sentence summary,
so that I can catalogue podcast episodes and audio reports without listening to each one in full.
```

### PoC Web Application

```gherkin
As an editorial tester,
I want to drag-and-drop or select multiple files for upload on a single page,
so that I can evaluate the metadata generation quickly and conveniently.
```

```gherkin
As an editorial tester,
I want to see each file's extracted metadata displayed in a visual tile alongside a thumbnail or icon,
so that I can easily review and compare results at a glance.
```

### Production Integration

```gherkin
As a publishing system,
I want to call a webhook with a reference to a new media file,
so that metadata is generated automatically and returned for storage in our CMS without manual intervention.
```

---

## 6. Assumptions & Constraints

### Assumptions

- **[A-1]** Azure Content Understanding provides sufficient accuracy for German-language image and audio analysis to meet the quality thresholds defined in G-1 and G-2.
- **[A-2]** The PoC dataset (10–20 images, 2 audio files) is representative of the types of media the editorial team works with daily.
- **[A-3]** Internet connectivity to Azure cloud services is available in the target environment.
- **[A-4]** Stakeholders will provide sample images and audio files for the PoC evaluation.
- **[A-5]** The visual benchmark (*DIE RHEINPFALZ* website design) is used as directional inspiration, not a pixel-perfect replication target.

### Constraints

- **[C-1]** The PoC must use **Azure Content Understanding** as the AI service.
- **[C-2]** All generated output must be in **German**.
- **[C-3]** The PoC web application must be a **single-page application** — no multi-page navigation.
- **[C-4]** Production throughput must support at least **5 000 images per month**.
- **[C-5]** Production integration must be achievable via a **webhook-based** interface (no proprietary SDKs or agents required on the consuming side).

---

*This is a living document. It will be updated as new information, feedback, or decisions emerge.*
