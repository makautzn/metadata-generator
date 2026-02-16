# Installation

## Prerequisites

- **Python 3.12+** — Backend API runtime
- **Node.js 20+** — Frontend build toolchain
- **pnpm** — Frontend package manager
- **uv** — Python project manager
- **Azure Subscription** — Access to Azure Content Understanding

## Clone the Repository

```bash
git clone https://github.com/makautzn/metadata-generator.git
cd metadata-generator
```

## Backend Setup

```bash
cd MetadataGenerator.Api

# Install dependencies
uv sync --dev

# Copy environment variables
cp .env.example .env
# Edit .env and add your Azure Content Understanding credentials
```

## Frontend Setup

```bash
cd MetadataGenerator.Web

# Install dependencies
pnpm install

# Copy environment variables
cp .env.local.example .env.local
```

## Azure Content Understanding

1. Create an Azure Content Understanding resource in the [Azure Portal](https://portal.azure.com).
2. Copy the **endpoint** and **API key** from the resource's Keys and Endpoint page.
3. Add them to `MetadataGenerator.Api/.env`:

```env
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com
AZURE_CONTENT_UNDERSTANDING_KEY=<your-key>
```

## Verify Installation

```bash
# Backend
cd MetadataGenerator.Api
uv run pytest  # All tests should pass

# Frontend
cd MetadataGenerator.Web
pnpm test      # All tests should pass
```
