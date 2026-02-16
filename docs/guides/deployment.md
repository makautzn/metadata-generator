# Deployment

!!! note
    This document will be updated as deployment infrastructure is finalized.

## Overview

The Metadata Generator consists of two deployable services:

| Service | Technology | Deployment Target |
|---------|-----------|-------------------|
| Backend API | FastAPI (Python) | Azure App Service / Container Apps |
| Frontend | Next.js | Azure Static Web Apps / App Service |

## Prerequisites

- Azure subscription with appropriate permissions
- Azure Content Understanding resource provisioned
- Azure CLI installed and authenticated

## Environment Variables

Ensure all required environment variables are set in your deployment environment. See [Environment Variables](../reference/environment-variables.md) for a complete list.

## Build Commands

### Backend

```bash
cd MetadataGenerator.Api
uv sync --no-dev
```

### Frontend

```bash
cd MetadataGenerator.Web
pnpm install --frozen-lockfile
pnpm build
```

## Health Checks

Configure your deployment platform to monitor:

- **Liveness**: `GET /health` — returns `200` when the service is running
- **Readiness**: `GET /health/ready` — returns `200` when the service can accept traffic
