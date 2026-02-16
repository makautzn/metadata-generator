# Spec2Cloud - AI-Powered Development Workflows

Transform any project into a spec2cloud-enabled development environment with specialized GitHub Copilot agents and workflows.

## 🎯 What's Included

This package contains:

✅ **8 Specialized AI Agents**
- PM Agent - Product requirements and feature planning
- Dev Lead Agent - Technical architecture and standards
- Dev Agent - Implementation and code generation  
- Azure Agent - Cloud deployment and infrastructure
- Reverse Engineering Agent - Codebase documentation
- Modernization Agent - Technical debt and upgrades
- Planner Agent - Task breakdown and planning
- Architect Agent - System design and patterns

✅ **13 Workflow Prompts**
- `/prd` - Create Product Requirements Document
- `/frd` - Create Feature Requirements Documents
- `/plan` - Create Technical Task Breakdown
- `/implement` - Implement features locally
- `/delegate` - Delegate to GitHub Copilot Coding Agent
- `/deploy` - Deploy to Azure
- `/rev-eng` - Reverse engineer existing codebase
- `/modernize` - Create modernization plan
- `/generate-agents` - Generate agent guidelines
- `/architect` - Design system architecture
- `/prd-brown` - Generate PRD from existing code
- `/frd-brown` - Generate FRDs from existing code
- `/plan-brown` - Generate tasks from existing code

✅ **Additional Components** (Full Package Only)
- MCP server configuration for enhanced AI capabilities
- Dev container setup with all required tools
- APM (Agent Package Manager) template for standards
- Directory structure templates

## 🚀 Quick Start

### Installation

Run the installer script:

**Linux/Mac**:
```bash
# Full installation (recommended)
./scripts/install.sh --full

# Minimal installation (agents and prompts only)
./scripts/install.sh --agents-only

# Install to specific directory
./scripts/install.sh --full /path/to/your/project
```

**Windows**:
```powershell
# Full installation (recommended)
.\scripts\install.ps1 -Full

# Minimal installation (agents and prompts only)
.\scripts\install.ps1 -AgentsOnly

# Install to specific directory
.\scripts\install.ps1 -Full C:\path\to\your\project
```

### Verification

After installation:

1. Open your project in VS Code
2. Open GitHub Copilot Chat (`Ctrl+Shift+I` or `Cmd+Shift+I`)
3. Type `@` to see available agents
4. Type `/` to see available workflows

You should see all 8 agents and 13 prompts listed.

## 📖 Usage

### Greenfield (New Features)

Build new features from product ideas:

```
1. /prd       → Define product vision and requirements
2. /frd       → Break down into features
3. /plan      → Create technical tasks
4. /implement → Write the code
5. /deploy    → Deploy to Azure
```

### Brownfield (Existing Code)

Document and modernize existing codebases:

```
1. /rev-eng   → Reverse engineer into documentation
2. /modernize → (Optional) Create modernization plan
3. /plan      → (Optional) Implement modernization
4. /deploy    → (Optional) Deploy to Azure
```

## 📁 Directory Structure

After installation, your project will have:

```
your-project/
├── .github/
│   ├── agents/              # AI agent definitions
│   └── prompts/             # Workflow prompts
├── .vscode/
│   └── mcp.json            # MCP configuration (full install)
├── .devcontainer/
│   └── devcontainer.json   # Dev container (full install)
├── specs/                   # Generated documentation
│   ├── features/
│   ├── tasks/
│   └── docs/
└── apm.yml                 # APM config (full install)
```

## 🔧 Configuration

### MCP Servers (Full Install)

Model Context Protocol servers provide enhanced capabilities:
- **context7** - Up-to-date library documentation
- **github** - Repository management
- **microsoft.docs.mcp** - Microsoft/Azure docs
- **playwright** - Browser automation

Requires: Docker, uvx, Node.js

### Dev Container (Full Install)

Pre-configured development container includes:
- Python 3.12
- Node.js and TypeScript
- Azure CLI & Azure Developer CLI
- Docker-in-Docker
- VS Code extensions (Copilot, Azure, AI Toolkit)

### APM - Agent Package Manager (Full Install)

Manage engineering standards across projects:

```bash
# Install standards
apm install

# Generate consolidated agent guidelines
apm compile
```

## 🎓 Examples

### Example 1: New Feature

```
User: "I want to add user authentication to my app"

@pm /prd
→ Creates PRD with authentication requirements

@pm /frd  
→ Breaks down into login, signup, password reset features

@dev /plan
→ Creates technical tasks for each feature

@dev /implement
→ Implements authentication code

@azure /deploy
→ Deploys to Azure with proper security
```

### Example 2: Document Legacy Code

```
User: "I inherited a Python app with no documentation"

@rev-eng /rev-eng
→ Analyzes codebase, creates comprehensive documentation
→ Generates tasks, features, and product vision

@modernize /modernize
→ Identifies modernization opportunities
→ Creates upgrade plan for dependencies and architecture
```

## ⚙️ Installation Options

| Flag | Description |
|------|-------------|
| `--full` / `-Full` | Install all components (recommended) |
| `--agents-only` / `-AgentsOnly` | Install only agents and prompts |
| `--merge` / `-Merge` | Merge with existing files (default) |
| `--force` / `-Force` | Overwrite without prompting |

## 🔍 Troubleshooting

### Agents Not Showing
- Reload VS Code: `Ctrl+Shift+P` → "Reload Window"

### MCP Servers Not Loading
- Check `.vscode/mcp.json` configuration
- Verify Docker, uvx, Node.js are installed
- Restart VS Code

### Permission Issues
```bash
chmod +x scripts/install.sh
```

### Conflicting Configurations
- Check for `*.spec2cloud` files
- Manually merge with your existing configs
- Delete `.spec2cloud` files after merging

## 📚 Learn More

- **Integration Guide**: See `INTEGRATION.md` for detailed setup instructions
- **GitHub Repository**: https://github.com/EmeaAppGbb/spec2cloud
- **APM Documentation**: https://github.com/danielmeppiel/apm

## 🆘 Support

- **Documentation**: Check README.md and INTEGRATION.md
- **Issues**: Report bugs on GitHub
- **Discussions**: Ask questions on GitHub Discussions

## 📝 License

See LICENSE.md for details.

---

**Ready to start?** Run the installer and open your project in VS Code! 🚀

```bash
# Linux/Mac
./scripts/install.sh --full

# Windows
.\scripts\install.ps1 -Full
```
