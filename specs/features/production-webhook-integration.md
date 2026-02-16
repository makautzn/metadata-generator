# Feature: Production Webhook Integration

**Parent PRD:** [specs/prd.md](../prd.md)
**Requirements covered:** REQ-14, REQ-15, REQ-16

---

## 1. Overview

For production use, external systems (e.g., a CMS or media asset pipeline) must be able to trigger metadata extraction programmatically. This feature provides a webhook endpoint that accepts file references, processes them through the metadata extraction pipeline, and returns structured results in a consistent format.

---

## 2. Functional Requirements

### 2.1 Webhook Endpoint

| ID | Requirement |
|----|-------------|
| HOOK-1 | The system must expose an **HTTP-callable webhook endpoint** that triggers metadata extraction for a given media file. |
| HOOK-2 | The webhook must accept a **file reference** (e.g., URL or storage path) rather than requiring direct file upload in the request body. |
| HOOK-3 | The webhook must support both **image** and **audio** file types (same formats as the PoC). |
| HOOK-4 | The endpoint must be **idempotent** — calling it multiple times with the same file reference should produce the same result without side effects. |
| HOOK-5 | The webhook must support **batch requests** — accepting multiple file references in a single call and returning metadata for each. |

### 2.2 Response Format

| ID | Requirement |
|----|-------------|
| HOOK-6 | The webhook response must follow a **consistent, documented schema** that distinguishes between image and audio metadata fields. |
| HOOK-7 | The response for images must include: description, keywords, and caption. |
| HOOK-8 | The response for audio must include: description, keywords, and one-sentence summary. |
| HOOK-9 | Error responses must include a **machine-readable error code** and a **human-readable error message**. |

### 2.3 Scalability & Reliability

| ID | Requirement |
|----|-------------|
| HOOK-10 | The system must support **≥ 5 000 image processing requests per month** in production. |
| HOOK-11 | The system must handle **concurrent requests** without data corruption or lost jobs. |
| HOOK-12 | End-to-end processing per file must complete within **15 minutes** from request receipt to result delivery. |
| HOOK-13 | The system must use a **callback (push) pattern** — the caller provides a callback URL in the request, and the system posts results to that URL upon completion. |

### 2.4 Security

| ID | Requirement |
|----|-------------|
| HOOK-14 | The webhook endpoint must require **API key authentication** (key passed via a request header) to prevent unauthorized use. |
| HOOK-15 | The authentication mechanism must be simple enough for consuming systems to integrate without proprietary SDKs or agents. |

---

## 3. Acceptance Criteria

- An authorized external system can call the webhook with a file reference and receive structured metadata via the provided callback URL.
- A batch request with multiple file references is accepted and results are delivered for each file.
- Unsupported file types return a clear error response with an appropriate error code.
- The endpoint handles at least 5 concurrent requests without failure.
- The same file reference submitted twice returns the same metadata output.
- Results are delivered within 15 minutes of the request.
- Requests without a valid API key are rejected with an appropriate authentication error.

---

## 4. Resolved Questions

- **Should the webhook support batch requests (multiple files in a single call)?** — Yes, batch requests must be supported.
- **What is the preferred authentication mechanism?** — **API key** (passed via request header).
- **Should processed results be cached to avoid redundant AI calls for the same file?** — No, caching is not required.
- **What is the maximum acceptable end-to-end latency per file?** — **15 minutes** from request to result delivery.
- **Should the webhook deliver results via callback (push) or polling (pull)?** — **Push** via a caller-provided callback URL.
