# Haconiwa (箱庭) 🚧 **Under Development**

[![PyPI version](https://badge.fury.io/py/haconiwa.svg)](https://badge.fury.io/py/haconiwa)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-alpha--development-red)](https://github.com/dai-motoki/haconiwa)

**Haconiwa (箱庭)** is an AI collaborative development support Python CLI tool. This next-generation tool integrates tmux company management, git-worktree integration, task management, and AI agent coordination to provide an efficient development environment.

> ⚠️ **Note**: This project is currently under active development. Features and APIs may change frequently.

[🇯🇵 日本語版 README](README_JA.md)

## 📋 Version Management

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

- **📄 Changelog**: [CHANGELOG.md](CHANGELOG.md) - All version change history
- **🏷️ Latest Version**: 0.1.4
- **📦 PyPI**: [haconiwa](https://pypi.org/project/haconiwa/)
- **🔖 GitHub Releases**: [Releases](https://github.com/dai-motoki/haconiwa/releases)

## 🚀 Ready-to-Use Features

### tmux Multi-Agent Environment (Implemented)

Create and manage a 4x4 grid multi-agent development environment **right now**:

```bash
# 1. Installation
pip install haconiwa

# 2. Create multi-agent environment (4 organizations × 4 roles = 16 panes)
haconiwa space multiagent --name my-project \
  --base-path /path/to/workspace \
  --org01-name "Frontend Development" --task01 "UI Design" \
  --org02-name "Backend Development" --task02 "API Development" \
  --org03-name "Database Team" --task03 "Schema Design" \
  --org04-name "DevOps Team" --task04 "Infrastructure"

# 3. List companies
haconiwa space list

# 4. Attach to existing company
haconiwa space attach my-project

# 5. Update company settings (rename existing company)
haconiwa space multiagent --name my-project \
  --base-path /path/to/workspace \
  --org01-name "New Frontend Team" --task01 "React Development" \
  --no-attach

# 6. Terminate company
haconiwa space kill my-project
```

**📁 Auto-created Directory Structure:**
```
/path/to/workspace/
├── org-01/
│   ├── 01boss/          # PM workspace
│   ├── 01worker-a/      # Worker-A workspace
│   ├── 01worker-b/      # Worker-B workspace
│   └── 01worker-c/      # Worker-C workspace
├── org-02/
│   ├── 02boss/
│   ├── 02worker-a/
│   ├── 02worker-b/
│   └── 02worker-c/
├── org-03/ (same structure)
└── org-04/ (same structure)
```

**✅ Actually Working Features:**
- 🏢 **Multi-Agent Environment**: 4x4 (16 panes) organizational tmux layout
- 📁 **Auto Directory Structure**: Automatic workspace creation by organization/role
- 🏷️ **Custom Organization & Task Names**: Dynamic title configuration
- 🔄 **Company Updates**: Safe configuration changes for existing companies
- 📋 **Company Management**: Complete support for create/list/attach/delete
- 📄 **Auto README Generation**: Automatic README.md creation in each directory

## ✨ Key Features (In Development)

- 🤖 **AI Agent Management**: Create and monitor Boss/Worker agents
- 📦 **World Management**: Build and manage development environments  
- 🖥️ **tmux Company Integration**: Efficient development space management
- 📋 **Task Management**: Task management system integrated with git-worktree
- 📊 **Resource Management**: Efficient scanning of databases and file paths
- 👁️ **Real-time Monitoring**: Progress monitoring of agents and tasks

## 🏗️ Architecture Concepts

### tmux ↔ Haconiwa Concept Mapping

| tmux Concept | Haconiwa Concept | Description |
|-------------|------------------|-------------|
| **Session** | **Company** | Top-level management unit representing entire project |
| **Window** | **Room** | Functional work areas for specific roles and functions |
| **Pane** | **Desk** | Individual workspaces for concrete task execution |

### Logical Hierarchy Management

```
Company
├── Building         ← Logical management layer (tmux-independent)
│   └── Floor        ← Logical management layer (tmux-independent)
│       └── Room     ← tmux Window
│           └── Desk ← tmux Pane
```

**Logical Management Layer Features:**
- **Building**: Major project categories (Frontend Building, Backend Building, etc.)
- **Floor**: Functional classifications (Development Floor, Testing Floor, Deploy Floor, etc.)
- These layers are managed logically within haconiwa without direct tmux company mapping

### Organization Structure Model

```
Organization
├── PM (Project Manager)
│   ├── Overall coordination
│   ├── Task assignment
│   └── Progress management
└── Worker
    ├── Worker-A (Development)
    ├── Worker-B (Testing)
    └── Worker-C (Deployment)
```

**Role Definitions:**
- **PM (Boss)**: Strategic decision-making, resource management, quality assurance
- **Worker**: Implementation, testing, deployment and other execution tasks
- **Organization**: Logical team unit composed of multiple PMs/Workers

## 🚀 Installation

```bash
pip install haconiwa
```

> 📝 **Development Note**: The package is available on PyPI but many features are still in development.

## ⚡ Quick Start

> 🎭 **Important**: All commands shown below are **demonstration purposes only**. These commands currently display help information and basic structure, but the actual functionality is under development. We are actively working on implementing the full features.

### 1. View Available Commands
```bash
haconiwa --help
```

### 2. Initialize Project
```bash
haconiwa core init
```

### 3. Create Development World
```bash
haconiwa world create local-dev
```

### 4. Launch AI Agents
```bash
# Create boss agent
haconiwa agent spawn boss

# Create worker agent
haconiwa agent spawn worker-a
```

### 5. Task Management
```bash
# Create new task
haconiwa task new feature-login

# Assign task to agent
haconiwa task assign feature-login worker-a

# Monitor progress
haconiwa watch tail worker-a
```

## 📖 Command Reference

> 🔧 **Development Note**: The commands listed below are currently **for demonstration and testing purposes**. While the CLI structure is functional, most commands will show help information or placeholder responses. We are actively developing the underlying functionality for each command group.

The CLI tool provides 7 main command groups:

### `agent` - Agent Management Commands
Manage AI agents (Boss/Worker) for collaborative development
- `haconiwa agent spawn <type>` - Create agent
- `haconiwa agent ps` - List agents  
- `haconiwa agent kill <name>` - Stop agent

### `core` - Core Management Commands  
Core system management and configuration
- `haconiwa core init` - Initialize project
- `haconiwa core status` - Check system status
- `haconiwa core upgrade` - Upgrade system

### `resource` - Resource Management
Scan and manage project resources (databases, files, etc.)
- `haconiwa resource scan` - Scan resources
- `haconiwa resource list` - List resources

### `space` - Manage tmux Spaces and Companies
Efficient development workspace management via tmux
- `haconiwa space create <name>` - Create tmux company
- `haconiwa space list` - List companies
- `haconiwa space attach <name>` - Attach to company

### `task` - Task Management Commands
Task management integrated with git-worktree
- `haconiwa task new <name>` - Create new task
- `haconiwa task assign <task> <agent>` - Assign task
- `haconiwa task status` - Check task status

### `watch` - Monitoring Commands
Real-time monitoring of agents and tasks
- `haconiwa watch tail <target>` - Real-time monitoring
- `haconiwa watch logs` - View logs

### `world` - World Management
Development environment and world management
- `haconiwa world create <name>` - Create new development world
- `haconiwa world list` - List worlds
- `haconiwa world switch <name>` - Switch world

## 🛠️ Development Status

> 🎬 **Current Phase**: **Demonstration & Prototyping**  
> Most CLI commands are currently demonstration placeholders that show the intended structure and help information. We are actively developing the core functionality behind each command.

### ✅ Completed Features
- Basic CLI structure with 7 command groups
- PyPI package distribution and installation
- Core project initialization framework
- Help system and command documentation
- Command group organization and routing

### 🚧 In Development
- AI agent spawning and management (placeholder → real implementation)
- tmux company integration (placeholder → real implementation)
- Task management with git-worktree (placeholder → real implementation)
- Resource scanning functionality (placeholder → real implementation)
- Real-time monitoring system (placeholder → real implementation)
- World/environment management (placeholder → real implementation)

### 📋 Planned Features
- Advanced AI agent coordination
- Integration with popular development tools
- Plugin system for extensibility
- Web-based monitoring dashboard

## 🛠️ Development Environment Setup

```bash
git clone https://github.com/dai-motoki/haconiwa.git
cd haconiwa
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .[dev]
```

### Running Tests

```bash
pytest tests/
```

## 📝 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions to the project! Since this is an active development project, please:

1. Check existing issues and discussions
2. Fork this repository
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Create a Pull Request

## 📞 Support

- GitHub Issues: [Issues](https://github.com/dai-motoki/haconiwa/issues)
- Email: kanri@kandaquantum.co.jp

## ⚠️ Disclaimer

This project is in early alpha development and **demonstration phase**. Current CLI commands are primarily placeholders showing the intended interface design. Most functionality is under active development and not yet implemented.

**What works now:**
- CLI installation and command structure
- Help system and documentation
- Basic command routing

**What's coming:**
- Full implementation of all advertised features
- AI agent coordination functionality  
- Integration with development tools
- Real task and company management

Use in production environments is not recommended at this time. This is a development preview showcasing the intended user experience.

---

**Haconiwa (箱庭)** - The Future of AI-Collaborative Development 🚧