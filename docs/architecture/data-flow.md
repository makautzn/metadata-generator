# Data Flow

## Single File Analysis

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Next.js Frontend
    participant API as FastAPI Backend
    participant CU as Azure Content Understanding

    User->>Frontend: Upload file
    Frontend->>API: POST /api/v1/analyze/image (or /audio)
    API->>API: Validate file (type, size)
    API->>CU: Send file for analysis
    CU-->>API: Analysis result (description, keywords, caption/summary)
    API-->>Frontend: JSON response with metadata
    Frontend-->>User: Display metadata tile
```

## Batch Upload Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Next.js Frontend
    participant API as FastAPI Backend
    participant CU as Azure Content Understanding

    User->>Frontend: Upload multiple files (≤ 20)
    Frontend->>API: POST /api/v1/analyze/batch (multipart)
    loop For each file (concurrent)
        API->>CU: Analyze file
        CU-->>API: Result
    end
    API-->>Frontend: BatchAnalysisResponse (ordered results)
    Frontend-->>User: Display tile grid
```

## Webhook Integration Flow

```mermaid
sequenceDiagram
    participant CMS as External CMS
    participant API as FastAPI Backend
    participant CU as Azure Content Understanding

    CMS->>API: POST /api/v1/webhook/analyze (file URLs, callback URL)
    API-->>CMS: 202 Accepted (request_id)
    loop Background processing
        API->>API: Download file from URL
        API->>CU: Analyze file
        CU-->>API: Result
    end
    API->>CMS: POST callback URL (results payload)
```

## Data Models

### Image Metadata

| Field | Type | Description |
|-------|------|-------------|
| `description` | `string` | Detailed natural-language description (German) |
| `keywords` | `string[]` | Relevant tags for search and categorization |
| `caption` | `string` | Concise, publication-ready image subtitle |

### Audio Metadata

| Field | Type | Description |
|-------|------|-------------|
| `description` | `string` | Detailed summary of audio content (German) |
| `keywords` | `string[]` | Relevant tags for search and categorization |
| `summary` | `string` | One-sentence summary |
