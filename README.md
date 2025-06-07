# Haconiwa (箱庭) 🚧 **Under Development**

[![PyPI version](https://badge.fury.io/py/haconiwa.svg)](https://badge.fury.io/py/haconiwa)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-alpha--development-red)](https://github.com/dai-motoki/haconiwa)

**Haconiwa (箱庭)** is an AI collaborative development support Python CLI tool. This next-generation tool integrates tmux session management, git-worktree integration, task management, and AI agent coordination to provide an efficient development environment.

> ⚠️ **Note**: This project is currently under active development. Features and APIs may change frequently.

[🇯🇵 日本語版 README](README_JA.md)

## ✨ Key Features (In Development)

- 🤖 **AI Agent Management**: Create and monitor Boss/Worker agents
- 📦 **World Management**: Build and manage development environments  
- 🖥️ **tmux Session Integration**: Efficient development space management
- 📋 **Task Management**: Task management system integrated with git-worktree
- 📊 **Resource Management**: Efficient scanning of databases and file paths
- 👁️ **Real-time Monitoring**: Progress monitoring of agents and tasks

## 🚀 Installation

```bash
pip install haconiwa
```

> 📝 **Development Note**: The package is available on PyPI but many features are still in development.

## ⚡ Quick Start

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

### `space` - Manage tmux Spaces and Sessions
Efficient development workspace management via tmux
- `haconiwa space create <name>` - Create tmux session
- `haconiwa space list` - List sessions
- `haconiwa space attach <name>` - Attach to session

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

### ✅ Completed Features
- Basic CLI structure with 7 command groups
- PyPI package distribution
- Core project initialization
- Help system and command documentation

### 🚧 In Development
- AI agent spawning and management
- tmux session integration
- Task management with git-worktree
- Resource scanning functionality
- Real-time monitoring system
- World/environment management

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

This project is in early alpha development. Features may be incomplete, unstable, or subject to significant changes. Use in production environments is not recommended at this time.

---

**Haconiwa (箱庭)** - The Future of AI-Collaborative Development 🚧