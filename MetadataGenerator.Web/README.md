# Metadata Generator Web

Frontend web application for the Metadata Generator PoC, built with **Next.js**, **TypeScript**, and **Tailwind CSS**.

## Quick Start

```bash
# Install dependencies
pnpm install

# Copy environment variables
cp .env.local.example .env.local

# Start dev server (http://localhost:3000)
pnpm dev
```

## Available Commands

| Command              | Description                               |
| -------------------- | ----------------------------------------- |
| `pnpm dev`           | Start dev server with hot-reload          |
| `pnpm build`         | Create production build                   |
| `pnpm start`         | Serve production build                    |
| `pnpm lint`          | ESLint + Prettier check                   |
| `pnpm lint:fix`      | Auto-fix lint & format issues             |
| `pnpm typecheck`     | TypeScript type-checking (`tsc --noEmit`) |
| `pnpm test`          | Run tests (Vitest)                        |
| `pnpm test:watch`    | Run tests in watch mode                   |
| `pnpm test:coverage` | Run tests with coverage report            |

## Project Structure

```
src/
├── app/              # Next.js App Router (layouts, pages)
├── components/       # Shared UI components
├── hooks/            # Custom React hooks
├── lib/              # Utilities, API client, types
├── styles/           # Design tokens and theme
└── test/             # Test setup and utilities
```

## Tech Stack

- **Next.js 16** — React framework with App Router
- **React 19** — UI library
- **TypeScript 5** — Type-safe development (strict mode)
- **Tailwind CSS 4** — Utility-first styling
- **Vitest** — Unit testing
- **React Testing Library** — Component testing
- **ESLint + Prettier** — Linting and formatting
