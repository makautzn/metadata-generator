# 003 — Documentation Scaffolding (MkDocs)

## Description

Set up the MkDocs documentation site with Material theme following the documentation standards in AGENTS.md. Create the required folder structure, configuration file, and initial documentation pages.

## Dependencies

- None (can proceed in parallel with 001 and 002)

## Technical Requirements

### MkDocs Configuration

- Create `mkdocs.yml` at the repository root with Material theme configuration as specified in AGENTS.md
- Configure site name: "Metadata Generator"
- Configure repo URL pointing to the GitHub repository
- Enable features: navigation tabs, search, code copy, code annotate
- Configure dark/light mode toggle

### Documentation Structure

Create the following files with appropriate initial content:

```
docs/
├── index.md                        # Landing page: project overview, quick links
├── getting-started/
│   ├── installation.md             # Prerequisites, setup instructions
│   ├── quick-start.md              # 5-minute guide to run the PoC
│   └── configuration.md            # Environment variables, Azure setup
├── architecture/
│   ├── overview.md                 # High-level architecture diagram (Mermaid)
│   ├── system-design.md            # Component descriptions, technology choices
│   └── data-flow.md                # File upload → AI processing → metadata response
├── api/
│   ├── rest-api.md                 # API endpoints documentation
│   └── webhook-api.md              # Webhook contract documentation
├── guides/
│   ├── development.md              # Dev workflow, commands, conventions
│   ├── deployment.md               # Azure deployment procedures
│   └── troubleshooting.md          # Common issues and solutions
└── reference/
    ├── configuration.md            # Full configuration reference
    └── environment-variables.md    # All env vars with descriptions
```

### ADR Directory

- Create `specs/adr/` directory
- Add `0001-use-mkdocs.md` following the MADR template (status: Accepted)

### Navigation

- Configure `nav` in `mkdocs.yml` matching the folder structure above

## Acceptance Criteria

- [x] `mkdocs serve` runs without errors
- [x] `mkdocs build --strict` passes without warnings
- [x] All pages render correctly with Material theme
- [x] Dark/light mode toggle works
- [x] Search functionality is operational
- [x] Navigation structure matches the documentation plan
- [x] `specs/adr/0001-use-mkdocs.md` exists and follows MADR format
- [x] Architecture overview includes a Mermaid diagram placeholder

## Testing Requirements

- Validation: `mkdocs build --strict` passes as a quality gate
- Validation: all internal links resolve correctly
- Validation: no broken navigation entries
