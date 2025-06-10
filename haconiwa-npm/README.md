# Haconiwa (箱庭) - npm package 🚧 **Coming Soon**

[![npm version](https://img.shields.io/badge/npm-coming%20soon-orange)](https://www.npmjs.com/package/haconiwa)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Haconiwa (箱庭)** is an AI collaborative development support CLI tool. This npm package will provide a Node.js wrapper for the Python haconiwa package, allowing you to use haconiwa commands seamlessly in Node.js environments.

> 🚧 **Status**: This npm package is currently under development and will be published soon!  
> 📦 **Note**: This will be a wrapper package. The actual implementation is in Python. You will need to install the Python package separately.

## 📋 Current Status

**✅ Python Package Available Now:**
```bash
pip install haconiwa --upgrade
```

**🚧 npm Package Coming Soon:**
- Node.js wrapper for Python haconiwa
- Programmatic API for Node.js applications
- CLI compatibility with global installation
- Cross-platform support (Windows, macOS, Linux)

## 🚀 What's Coming (Planned Features)

### Global Installation (Coming Soon)

```bash
# This will be available soon!
npm install -g haconiwa
```

### Local Installation (Coming Soon)

```bash
# This will be available soon!
npm install haconiwa
```

### Usage with npx (Coming Soon)

```bash
# This will be available soon!
npx haconiwa --help
```

## ⚡ Planned Quick Start

### Command Line Usage (Coming Soon)

After global installation, you will be able to use `haconiwa` command directly:

```bash
# Check version
haconiwa --version

# Apply YAML configuration
haconiwa apply -f config.yaml

# Create company
haconiwa company build --name my-company

# List spaces
haconiwa space list
```

### Programmatic Usage (Coming Soon)

```javascript
const haconiwa = require('haconiwa');

// Check if haconiwa is available
if (haconiwa.isAvailable()) {
  console.log('Haconiwa is available!');
} else {
  console.log('Please install: pip install haconiwa');
}

// Execute commands programmatically
async function example() {
  try {
    // Get version
    const version = await haconiwa.getVersion();
    console.log('Haconiwa version:', version);
    
    // Apply YAML configuration
    const result = await haconiwa.commands.apply('config.yaml', {
      forceClone: true,
      noAttach: true
    });
    
    if (result.success) {
      console.log('Configuration applied successfully!');
    }
    
    // List spaces
    const spaces = await haconiwa.commands.listSpaces();
    console.log('Spaces:', spaces.stdout);
    
    // Build company
    await haconiwa.commands.buildCompany('my-company', {
      basePath: './workspace',
      noAttach: true
    });
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

example();
```

### Advanced Programmatic Usage (Coming Soon)

```javascript
const haconiwa = require('haconiwa');

// Execute any haconiwa command
async function customCommand() {
  const result = await haconiwa.exec([
    'space', 'run', 
    '-c', 'my-company', 
    '--claude-code'
  ]);
  
  console.log('Exit code:', result.code);
  console.log('Output:', result.stdout);
  console.log('Errors:', result.stderr);
  console.log('Success:', result.success);
}

// With custom spawn options
async function withCustomOptions() {
  const result = await haconiwa.exec(['--help'], {
    stdio: 'inherit', // Show output in real-time
    cwd: process.cwd()
  });
}
```

## 🔧 Planned API Reference

### `haconiwa.isAvailable()`
Check if the Python haconiwa package is available.

**Returns**: `boolean | string` - Installation type or `false` if not available

### `haconiwa.getVersion()`
Get the haconiwa version.

**Returns**: `Promise<string>` - Version string

### `haconiwa.exec(args, options)`
Execute a haconiwa command programmatically.

**Parameters**:
- `args` (Array): Command arguments
- `options` (Object): Spawn options

**Returns**: `Promise<Object>` - Command result with `code`, `signal`, `stdout`, `stderr`, and `success`

### `haconiwa.commands`

Pre-defined command shortcuts:

#### `haconiwa.commands.apply(file, options)`
Apply YAML configuration.

#### `haconiwa.commands.listSpaces(options)`
List spaces.

#### `haconiwa.commands.buildCompany(name, options)`
Build company.

#### `haconiwa.commands.deleteSpace(company, options)`
Delete space.

## 🏗️ Planned Development Features

This npm package will provide:

- 🔄 **Automatic Detection**: Finds Python haconiwa installation automatically
- 🛡️ **Error Handling**: Graceful error handling and user-friendly messages
- 📦 **Multiple Python Support**: Works with `python`, `python3`, and direct `haconiwa` commands
- 🎯 **CLI Compatibility**: 100% compatible with Python haconiwa CLI
- ⚡ **Programmatic API**: Use haconiwa from Node.js applications
- 🔧 **TypeScript Ready**: Will include TypeScript definitions

## 🚀 Current Ready-to-Use Features (Python Package)

While waiting for the npm package, you can use the Python package directly:

### Apply YAML Pattern (v1.0 Available Now)

```bash
# Install Python package
pip install haconiwa --upgrade

# Download sample configuration
curl -O https://raw.githubusercontent.com/dai-motoki/haconiwa/main/haconiwa-multiroom-test.yaml

# Apply configuration
haconiwa apply -f haconiwa-multiroom-test.yaml

# List created spaces
haconiwa space list

# Delete space
haconiwa space delete -c test-multiroom-company --clean-dirs --force
```

### Company Management (Available Now)

```bash
# Create company
haconiwa company build --name my-company \
  --org01-name "Frontend Team" --task01 "UI Development" \
  --org02-name "Backend Team" --task02 "API Development"

# List companies
haconiwa company list

# Delete company
haconiwa company kill my-company --force
```

## 📚 Documentation

For current documentation, see the main repository:

- **GitHub**: [https://github.com/dai-motoki/haconiwa](https://github.com/dai-motoki/haconiwa)
- **Python Package**: [https://pypi.org/project/haconiwa/](https://pypi.org/project/haconiwa/)

## 🚧 Development Progress

**✅ Completed:**
- Python package fully functional (v0.4.0 available on PyPI)
- Apply YAML pattern with multiroom support
- Company build and management system
- Task assignment with git-worktree integration

**🚧 In Progress:**
- npm package wrapper development
- Node.js API design and implementation
- Cross-platform compatibility testing
- Documentation preparation

**📋 Coming Next:**
- npm package publication
- TypeScript definitions
- Integration examples
- CI/CD pipeline for npm releases

## 📞 Support & Updates

- GitHub Issues: [https://github.com/dai-motoki/haconiwa/issues](https://github.com/dai-motoki/haconiwa/issues)
- Email: kanri@kandaquantum.co.jp

**📢 Stay Updated:**
- Watch the [GitHub repository](https://github.com/dai-motoki/haconiwa) for npm package release announcements
- Star the repo to get notified when the npm package becomes available

## 📝 License

MIT License - See [LICENSE](https://github.com/dai-motoki/haconiwa/blob/main/LICENSE) file for details.

## 🤝 Contributing

This npm package is part of the main haconiwa project. Please contribute to the main repository:

[https://github.com/dai-motoki/haconiwa](https://github.com/dai-motoki/haconiwa)

---

**Haconiwa (箱庭)** - The Future of AI Collaborative Development 🚧

> 💡 **Coming Soon**: npm package for seamless Node.js integration! 