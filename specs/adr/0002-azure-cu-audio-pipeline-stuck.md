# Azure Support Ticket — Content Understanding Audio Pipeline Stuck in "Running"

Date: 2026-03-05

## Issue Summary

All audio analysis operations submitted to Azure Content Understanding remain indefinitely stuck in "Running" status. They never transition to "Succeeded" or "Failed". This affects **all** audio analyzers (prebuilt and custom) on the resource. Image analysis via Content Understanding works correctly (~30s). The Speech-to-Text service on the same resource also works perfectly (<1s).

---

## Operation IDs

All operations were submitted on **2026-03-05** and remain in "Running" status after 60+ seconds (and in some cases 30+ minutes).

### Fresh operations (submitted 2026-03-05T16:37 UTC)

| Analyzer | Result ID | Submitted (UTC) | Status after 60s |
|----------|-----------|------------------|------------------|
| `audioMetadataExtractor` (custom, base: `prebuilt-audio`) | `827fed41-dfb7-488f-b1e5-41eae41051fa` | 2026-03-05T16:37:39Z | Running |
| `prebuilt-audio` | `6560baa1-ff10-4ef8-a613-d7613ea9779c` | 2026-03-05T16:37:39Z | Running |
| `prebuilt-audioSearch` (base: `prebuilt-audio`) | `25cdd19f-0cec-407d-afb6-f9e469650d15` | 2026-03-05T16:37:40Z | Running |

### Earlier operations from same session (also never completed)

| Analyzer | Operation / Result ID | Submitted (UTC) | Notes |
|----------|-----------------------|------------------|-------|
| `audioMetadataExtractor` | `a7d05260-467b-44ac-a277-a7027771328a` | ~2026-03-05T15:53:34Z | Still "Running" after 30+ minutes |
| `prebuilt-audioSearch` | `05ab9fb2-c768-4b21-84f3-a9a9914f0d0e` | ~2026-03-05T16:00Z | Timed out after 122s, still "Running" |
| `prebuilt-callCenter` | `91c6f49d-643f-457f-94fb-ee329856c3e0` | ~2026-03-05T16:00Z | Timed out after 122s, still "Running" |
| `audioMetadataExtractor` (rebuilt) | `0cdcc3fa-227d-4b5e-9ecd-eeffbf61ae32` | ~2026-03-05T16:10Z | Still "Running" after 136s |

### Operation-Location URL format

```
https://mk-foundry-exp.services.ai.azure.com/contentunderstanding/analyzerResults/{resultId}?api-version=2025-11-01
```

---

## Analyzer IDs and Configurations

| Analyzer ID | Base Analyzer | Status | Processing Location | Config |
|-------------|---------------|--------|---------------------|--------|
| `audioMetadataExtractor` | `prebuilt-audio` | ready | geography | `{"locales": ["de-DE", "en-US"], "returnDetails": true}` |
| `prebuilt-audio` | *(root)* | ready | geography | `{"returnDetails": false}` |
| `prebuilt-audioSearch` | `prebuilt-audio` | ready | geography | `{"returnDetails": true}` |

Completion model configured: `gpt-4.1-mini`

---

## Region and Endpoint

| Property | Value |
|----------|-------|
| **Endpoint** | `https://mk-foundry-exp.services.ai.azure.com` |
| **Resource type** | Azure AI Foundry hub/project |
| **Processing location** | `geography` (all analyzers) |
| **Authentication** | Entra ID (`DefaultAzureCredential`) |

---

## API Version and SDK

| Property | Value |
|----------|-------|
| **API version** | `2025-11-01` (GA) |
| **SDK** | `azure-ai-contentunderstanding==1.0.0b1` (Python) |
| **Submission endpoint** | `POST /contentunderstanding/analyzers/{analyzerId}:analyzeBinary` |
| **Content-Type header** | `audio/mpeg` (MP3) or `audio/wav` (WAV) |

---

## Sample Audio Metadata

*(Audio files are not attached — only technical metadata is provided.)*

| File | Format | Codec | Duration | Sample Rate | Channels | Bitrate | File Size |
|------|--------|-------|----------|-------------|----------|---------|-----------|
| `speech_01_de_short.mp3` | MPEG Audio | MP3 (Layer 3) | 2.83s | 24,000 Hz | 1 (mono) | 64 kbps | 22,656 bytes |
| `speech_02_de_medium.mp3` | MPEG Audio | MP3 (Layer 3) | 9.74s | 24,000 Hz | 1 (mono) | 64 kbps | 77,952 bytes |
| `tone_01_1s.wav` | WAV (RIFF) | PCM uncompressed | 1.0s | 44,100 Hz | 1 (mono) | 16-bit | 88,244 bytes |

- MP3 files contain German and English speech generated via gTTS.
- WAV files contain pure sine wave tones.
- All files are well under the documented 300 MB / 2-hour limit.

---

## Diagnostic Evidence

### What works on this resource

| Service | Test | Result |
|---------|------|--------|
| **Speech-to-Text** (Fast Transcription API) | `POST /speechtotext/transcriptions:transcribe?api-version=2024-11-15` with `speech_01_de_short.mp3` | **200 OK** in <1s — transcribed "Hallo, dies ist ein kurzer Test." with 0.99 confidence |
| **Image analysis** (Content Understanding) | `imageMetadataExtractor` (base: `prebuilt-image`) | **Succeeded** in ~30s — returns Description, Caption, Keywords |
| **Azure OpenAI** (AI Foundry inference) | `gpt-4o` via `/models/chat/completions` | **200 OK** — works correctly |
| **Speech base models** | `GET /speechtotext/v3.2/models/base` | **200 OK** — 100 models available |

### What does NOT work

| Service | Test | Result |
|---------|------|--------|
| **Audio analysis** (Content Understanding) | `prebuilt-audio` with any audio file | Accepted (202) but **stuck in "Running" indefinitely** |
| **Audio analysis** (Content Understanding) | `prebuilt-audioSearch` with any audio file | Accepted (202) but **stuck in "Running" indefinitely** |
| **Audio analysis** (Content Understanding) | `prebuilt-callCenter` with any audio file | Accepted (202) but **stuck in "Running" indefinitely** |
| **Audio analysis** (Content Understanding) | Custom `audioMetadataExtractor` with any audio file | Accepted (202) but **stuck in "Running" indefinitely** |

### Reproduction steps

1. Authenticate with `DefaultAzureCredential` (Entra ID).
2. Submit any audio file (MP3 or WAV, 1s to 60s, speech or tone) to:
   ```
   POST https://mk-foundry-exp.services.ai.azure.com/contentunderstanding/analyzers/prebuilt-audio:analyzeBinary?api-version=2025-11-01
   Content-Type: audio/mpeg
   ```
3. Receive `202 Accepted` with an `Operation-Location` header.
4. Poll the `Operation-Location` URL — status remains `"Running"` indefinitely (tested up to 30+ minutes).
5. The operation never transitions to `"Succeeded"` or `"Failed"`.

### Remediation attempts (all unsuccessful)

- Tested 3 different prebuilt analyzers (`prebuilt-audio`, `prebuilt-audioSearch`, `prebuilt-callCenter`)
- Tested custom analyzer with explicit `locales: ["de-DE", "en-US"]`
- Deleted and recreated the custom analyzer
- Tested MP3 (speech) and WAV (sine tone) formats
- Tested files from 1s to 60s duration
- Tested via SDK (`begin_analyze_binary`) and direct REST API
- Reduced polling interval to 5s (ruled out polling issues)

---

## Conclusion

The Content Understanding audio orchestration layer appears to be non-functional on this endpoint. The underlying Speech-to-Text service works perfectly when called directly, and image analysis via Content Understanding also works. The issue is isolated to how Content Understanding invokes/orchestrates the speech pipeline for audio analysis.
