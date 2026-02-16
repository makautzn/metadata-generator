
# spec2cloud

**Spec2Cloud** is an AI-powered development workflow that transforms high-level product ideas into production-ready applications deployed on Azure—using specialized GitHub Copilot agents working together.

## 🎯 Overview

This repository provides a preconfigured development environment and agent-driven workflow that works in two directions:

- **Greenfield (Build New)**: Transform product ideas into deployed applications through structured specification-driven development

https://github.com/user-attachments/assets/f0529e70-f437-4a14-93bc-4ab5a0450540


- **Greenfield (Shell-Based)**: Start from a predefined “shell” baseline and let coding agents translate natural language requirements to fill in the gaps via code.
   - https://github.com/EmeaAppGbb/shell-dotnet
   - https://github.com/EmeaAppGbb/agentic-shell-dotnet
   - https://github.com/EmeaAppGbb/agentic-shell-python



- **Brownfield (Document Existing + Modernize)**: Reverse engineer existing codebases into comprehensive product and technical documentation and optionally modernize codebases

Both workflows use specialized GitHub Copilot agents working together to maintain consistency, traceability, and best practices.

## 🚀 Quick Start

### Option 1: Use This Repository as a Template (Full Environment)

**Greenfield (New Project)**:
1. **Use this repo as a template** - Click "Use this template" to create your own GitHub repository
2. **Open in Dev Container** - Everything is preconfigured in `.devcontainer/`
3. **Describe your app idea** - The more specific, the better
4. **Follow the workflow** - Use the prompts to guide specialized agents through each phase

**Brownfield (Existing Codebase)**:
1. **Use this repo as a template** - Click "Use this template" to create your own GitHub repository
2. **copy your existing codebase** into the new repository
3. **Open in Dev Container** - Everything is preconfigured in `.devcontainer/`
4. **Run `/rev-eng`** - Reverse engineer codebase into specs and documentation
5. **Run `/modernize`** - (optional) Create modernization plan and tasks
6. **Run `/plan`** - (optional) Execute modernization tasks planned by the modernization agent

### Option 2: Install Into Existing Project using VSCode Extension

TODO

### Option 3: Install Into Existing Project using APM CLI

TODO

### Option 4: Install Into Existing Project using Manual Script

Transform any existing project into a spec2cloud-enabled development environment:

**One-Line Install** (Recommended):
```bash
curl -fsSL https://raw.githubusercontent.com/EmeaAppGbb/spec2cloud/main/scripts/quick-install.sh | bash
```

**Manual Install**:
```bash
# Download latest release
curl -L https://github.com/EmeaAppGbb/spec2cloud/releases/latest/download/spec2cloud-full-latest.zip -o spec2cloud.zip
unzip spec2cloud.zip -d spec2cloud
cd spec2cloud

# Run installer
./scripts/install.sh --full                    # Linux/Mac
.\scripts\install.ps1 -Full                    # Windows

# Start using workflows
code .
# Use @pm, @dev, @azure agents and /prd, /frd, /plan, /deploy prompts
```

**What Gets Installed**:
- ✅ 8 specialized AI agents (PM, Dev Lead, Dev, Azure, Rev-Eng, Modernizer, Planner, Architect)
- ✅ 13 workflow prompts
- ✅ MCP server configuration (optional)
- ✅ Dev container setup (optional)
- ✅ APM configuration (optional)

See **[INTEGRATION.md](INTEGRATION.md)** for detailed installation options and troubleshooting.


## 📚 Documentation

Longer guides are in the `docs/` folder (MkDocs-ready structure).

- Docs index: [docs/index.md](docs/index.md)
- Shell baselines: [docs/shells.md](docs/shells.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Workflows: [docs/workflows.md](docs/workflows.md)
- Generated docs structure: [docs/specs-structure.md](docs/specs-structure.md)
- Standards / APM: [docs/apm.md](docs/apm.md)
- Examples: [docs/examples.md](docs/examples.md)
- Benefits: [docs/benefits.md](docs/benefits.md)

For installation/integration scenarios, see [INTEGRATION.md](INTEGRATION.md).

## 🤝 Contributing

Contributions welcome! Extend with additional agents, prompts, or MCP servers.

---

**From idea to production in minutes, not months.** 🚀
