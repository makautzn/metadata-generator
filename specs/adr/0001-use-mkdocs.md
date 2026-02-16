# 1. Use MkDocs with Material Theme for Documentation

Date: 2025-07-21

## Status

Accepted

## Context and Problem Statement

The project needs a documentation framework that supports Markdown authoring, is easy to maintain alongside source code, and produces a professional, searchable documentation site.

## Decision Drivers

* Documentation must live in the repository alongside code
* Must support Markdown natively for low-friction authoring
* Must produce a static site that can be deployed to GitHub Pages
* Must support search, code highlighting, and diagrams (Mermaid)
* Must align with AGENTS.md documentation standards

## Considered Options

* **MkDocs with Material theme** — Python-based static site generator with rich Markdown extensions
* **Docusaurus** — React-based documentation framework by Meta
* **VitePress** — Vue-powered static site generator
* **Plain Markdown in GitHub** — No build step, rendered by GitHub

## Decision Outcome

Chosen option: **MkDocs with Material theme**, because it is Markdown-native, mandated by project engineering standards (AGENTS.md), provides an excellent developer experience with live reload, and has built-in support for search, admonitions, code highlighting, and Mermaid diagrams without additional bundler configuration.

### Consequences

**Positive:**

* Consistent with AGENTS.md documentation standards
* Fast build times and instant live reload during authoring
* Rich feature set (dark/light mode, tabs, search, code copy) with minimal configuration
* Python-based toolchain aligns with the backend stack
* Git revision date plugin provides automatic "last updated" metadata

**Negative:**

* Requires a Python virtual environment for documentation tooling (separate from the backend venv)
* Additional CI step needed for documentation deployment
* Team members unfamiliar with MkDocs need brief onboarding
