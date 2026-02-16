# 002 — Frontend Web App Scaffolding

## Description

Set up the Next.js 14 frontend application with TypeScript, the project folder structure, linting/formatting tooling, and a base layout shell. This task establishes the foundation that all frontend feature tasks build upon.

## Dependencies

- None (can proceed in parallel with 001)

## Technical Requirements

### Project Structure

```
MetadataGenerator.Web/
├── app/
│   ├── layout.tsx              # Root layout with metadata, fonts, global styles
│   ├── page.tsx                # Single-page entry point (upload + tile view)
│   └── globals.css             # Global styles and CSS custom properties
├── components/                 # Shared UI components (empty initially)
│   └── .gitkeep
├── hooks/                      # Custom React hooks (empty initially)
│   └── .gitkeep
├── lib/                        # Utility functions, API client, types
│   ├── api-client.ts           # Typed fetch wrapper for backend API
│   └── types.ts                # Shared TypeScript types/interfaces
├── public/                     # Static assets
│   └── .gitkeep
├── styles/                     # Theme tokens and design variables
│   └── theme.ts                # Design tokens (colors, typography, spacing)
├── .eslintrc.js or eslint.config.js
├── .prettierrc
├── next.config.js
├── package.json
├── tsconfig.json
└── README.md
```

### TypeScript Configuration

- Enable strict mode: `strict: true`, `noUncheckedIndexedAccess: true`, `noImplicitOverride: true`
- Target ESNext with module resolution "bundler"
- Path aliases: `@/` maps to project root

### API Client

- Create a typed fetch wrapper in `lib/api-client.ts` that:
  - Points to the backend API base URL (configurable via environment variable `NEXT_PUBLIC_API_URL`)
  - Provides typed request/response methods for `GET`, `POST`, `PUT`, `DELETE`
  - Handles error responses consistently
  - Includes proper TypeScript generics for type safety

### Base Layout

- Root layout with page metadata (title: "Metadata Generator", description)
- Import a clean sans-serif web font (e.g., Inter or similar) consistent with editorial design
- Minimal header with application title
- Main content area placeholder

### Dev Tooling

- Use `pnpm` as package manager
- Configure ESLint (flat config), Prettier, and Stylelint
- Add scripts: `dev`, `build`, `lint`, `typecheck`, `test`
- Install and configure Vitest + React Testing Library for unit tests

### Environment

- `.env.local.example` with `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`

## Acceptance Criteria

- [x] `pnpm install` completes without errors
- [x] `pnpm dev` starts the dev server and renders the base layout
- [x] `pnpm build` produces a production build without errors
- [x] `pnpm lint` passes with no errors
- [x] `pnpm typecheck` (`tsc --noEmit`) passes with no errors
- [x] `pnpm test` runs and all scaffold tests pass
- [x] TypeScript strict mode is fully enabled
- [x] API client module exists with typed methods
- [x] Environment variable example file is present
- [x] Page renders a header and empty content area

## Testing Requirements

- Unit test: API client correctly constructs request URLs
- Unit test: API client handles error responses
- Unit test: root layout renders without errors
- Unit test: page component renders without errors
- Snapshot test: base layout matches expected structure
- Coverage: ≥ 85% for scaffolding code
