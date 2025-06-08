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
- **🏷️ Latest Version**: 0.2.0
- **📦 PyPI**: [haconiwa](https://pypi.org/project/haconiwa/)
- **🔖 GitHub Releases**: [Releases](https://github.com/dai-motoki/haconiwa/releases)

## 🚀 Ready-to-Use Features

### tmux Multi-Agent Environment (Implemented)

Create and manage a 4x4 grid multi-agent development environment **right now**:

```bash
# 1. Installation
pip install haconiwa

# 2. Create multi-agent environment (4 organizations × 4 roles = 16 panes)
haconiwa company multiagent --name my-project \
  --base-path /path/to/desks \
  --org01-name "Frontend Development" --task01 "UI Design" \
  --org02-name "Backend Development" --task02 "API Development" \
  --org03-name "Database Team" --task03 "Schema Design" \
  --org04-name "DevOps Team" --task04 "Infrastructure"

# 3. List companies
haconiwa company list

# 4. Attach to existing company
haconiwa company attach my-project

# 5. Update company settings (rename existing company)
haconiwa company multiagent --name my-project \
  --base-path /path/to/desks \
  --org01-name "New Frontend Team" --task01 "React Development" \
  --no-attach

# 6. Terminate company
haconiwa company kill my-project
```

**📁 Auto-created Directory Structure:**
```
/path/to/desks/
├── org-01/
│   ├── 01boss/          # PM desk
│   ├── 01worker-a/      # Worker-A desk
│   ├── 01worker-b/      # Worker-B desk
│   └── 01worker-c/      # Worker-C desk
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
- 🏗️ **Auto Directory Structure**: Automatic desk creation by organization/role
- 🏷️ **Custom Organization & Task Names**: Dynamic title configuration
- 🔄 **Company Updates**: Safe configuration changes for existing companies
- 🏛️ **Company Management**: Complete support for create/list/attach/delete
- 📄 **Auto README Generation**: Automatic README.md creation in each desk

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