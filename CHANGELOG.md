# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2025-01-06

### Added
- 📖 **Ready-to-Use Features section** in README (both Japanese and English)
- 📁 **Directory structure documentation** with `--base-path` option explanation
- 🏗️ **Architecture Concepts section** explaining tmux ↔ Haconiwa concept mapping
- 📄 **Auto README generation** in each workspace directory
- 🏷️ **Terminology unification**: session → company throughout documentation

### Changed
- 🔄 **Concept terminology**: Unified "session" to "company" across all documentation
- 📋 **tmux Session** → **Haconiwa Company** concept mapping clarification
- 🏢 **Building/Floor logical hierarchy** management explanation

### Fixed
- 📝 Missing `--base-path` parameter in usage examples
- 🏷️ Inconsistent terminology between session and company

## [0.1.3] - 2025-01-06

### Added
- 🚀 **Complete tmux multiagent environment** (4x4 grid layout)
- 🏢 **Custom organization names** via `--org01-name`, `--org02-name`, etc.
- 🏷️ **Custom task names** via `--task01`, `--task02`, etc.
- 📁 **Automatic directory structure creation** with organized workspaces
- 🔄 **Session update functionality** - safe updates without disrupting existing work
- 🏷️ **Intuitive title ordering**: Organization-Role-Task format
- 📋 **Reliable attach/list commands** using direct tmux subprocess calls
- 📄 **README.md auto-generation** in each workspace directory

### Changed
- 🏷️ **Title order optimization**: From "ORG-01-BOSS-TaskName" to "OrganizationName-BOSS-TaskName"
- 🔧 **Session detection logic**: Automatic detection of existing sessions for update mode
- 🛡️ **Safety improvements**: Prevents overwriting existing directories and files

### Fixed
- 🔗 **Attach command reliability**: Replaced libtmux with direct tmux subprocess calls
- 📋 **List command accuracy**: Improved session status detection
- 🔄 **Update mode safety**: Preserves running processes during title updates

## [0.1.2] - 2025-01-05

### Added
- 🏗️ **Basic tmux session integration** foundation
- 📋 **CLI command structure** with 7 main command groups
- 🎯 **Core project initialization** framework
- 📖 **Comprehensive help system** and command documentation

### Fixed
- 🔧 **Package installation** issues
- 📦 **PyPI distribution** configuration

## [0.1.1] - 2025-01-05

### Added
- 🚀 **Initial PyPI release**
- 📋 **Complete CLI structure** with all command groups
- 📖 **Documentation** (Japanese and English README)
- 🏗️ **Project foundation** and basic architecture

### Technical
- 🐍 **Python 3.8+** support
- 📦 **PyPI package** distribution setup
- 🔧 **Development tools** configuration (pytest, black, flake8, etc.)

## [0.1.0] - 2025-01-05

### Added
- 🎯 **Initial project setup**
- 📋 **CLI framework** with typer
- 🏗️ **Basic project structure**
- 📄 **License and documentation** foundation

[Unreleased]: https://github.com/dai-motoki/haconiwa/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/dai-motoki/haconiwa/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/dai-motoki/haconiwa/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/dai-motoki/haconiwa/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/dai-motoki/haconiwa/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/dai-motoki/haconiwa/releases/tag/v0.1.0 