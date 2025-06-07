# haconiwa CLI Reference

## Command Groups Overview

### Core Commands
- `haconiwa core init` - Initialize haconiwa environment
- `haconiwa core status` - Show system status
- `haconiwa core reset` - Reset environment to initial state
- `haconiwa core upgrade` - Upgrade haconiwa version

### World Commands
- `haconiwa world create <name>` - Create new development world
- `haconiwa world list` - List available worlds
- `haconiwa world enter <name>` - Enter specified world
- `haconiwa world destroy <name>` - Destroy specified world
- `haconiwa world export <name>` - Export world configuration
- `haconiwa world import <file>` - Import world from configuration

### Space Commands
- `haconiwa space create` - Create new tmux session
- `haconiwa space attach` - Attach to existing session
- `haconiwa space resize` - Resize tmux panes
- `haconiwa space kill` - Kill tmux session
- `haconiwa space list` - List active sessions
- `haconiwa space layout <preset>` - Apply layout preset

### Resource Commands
- `haconiwa resource scan <path>` - Scan filesystem resources
- `haconiwa resource pull <query>` - Pull data from database
- `haconiwa resource sync` - Sync with remote storage
- `haconiwa resource cache` - Manage resource cache
- `haconiwa resource clean` - Clean unused resources
- `haconiwa resource export` - Export resource data

### Agent Commands
- `haconiwa agent spawn <type>` - Spawn new AI agent
- `haconiwa agent ps` - List running agents
- `haconiwa agent stop <id>` - Stop specified agent
- `haconiwa agent logs <id>` - Show agent logs
- `haconiwa agent shell <id>` - Open agent debug shell
- `haconiwa agent config <id>` - Configure agent settings

### Task Commands
- `haconiwa task new` - Create new development task
- `haconiwa task assign <id>` - Assign task to agent
- `haconiwa task show <id>` - Show task details
- `haconiwa task done <id>` - Mark task as completed
- `haconiwa task prune` - Clean up completed tasks
- `haconiwa task list` - List all tasks

### Watch Commands
- `haconiwa watch start` - Start monitoring daemon
- `haconiwa watch stop` - Stop monitoring daemon
- `haconiwa watch tail` - Show real-time metrics
- `haconiwa watch health` - Run health checks
- `haconiwa watch alert` - Manage alert rules
- `haconiwa watch report` - Generate monitoring report

## Common Options

```
Global Options:
  --verbose             Enable verbose output
  --config FILE         Use alternate config file
  --no-color           Disable colored output
  --quiet              Suppress all output
  --json               Output in JSON format
  --debug              Enable debug mode
```

## Usage Examples

### Command Line Usage

```bash
# Initialize new environment
haconiwa core init --config custom.yaml

# Create and enter development world
haconiwa world create dev-world
haconiwa world enter dev-world

# Start AI development workflow
haconiwa agent spawn boss
haconiwa task new "Implement login feature"
haconiwa task assign 1 worker-a
haconiwa watch start
```

### Python Script Usage

```python
from haconiwa.cli import app

# Initialize environment
app.run(["core", "init"])

# Create world programmatically
app.run(["world", "create", "dev-world"])

# Spawn agents
app.run(["agent", "spawn", "boss", "--config", "boss.yaml"])

# Monitor tasks
app.run(["watch", "start", "--metrics-port", "9090"])
```

## Configuration File (config.yaml)

```yaml
core:
  log_level: info
  data_dir: ~/.haconiwa
  backup_enabled: true

world:
  default_provider: local
  max_worlds: 5
  
agent:
  models:
    boss: gpt-4
    worker: gpt-3.5-turbo
  rate_limits:
    requests_per_minute: 60

watch:
  metrics_port: 9090
  alert_channels:
    - slack
    - email
```

## Environment Variables

```
haconiwa_CONFIG      Alternative config file path
haconiwa_LOG_LEVEL   Override logging level
haconiwa_DATA_DIR    Data directory location
haconiwa_NO_COLOR    Disable colored output if set
haconiwa_DEBUG       Enable debug mode if set
haconiwa_API_KEY     API key for AI services
```

## Error Handling

Commands return following exit codes:
- 0: Success
- 1: General error
- 2: Configuration error
- 3: Runtime error
- 4: User input error
- 5: System error

Errors include:
```python
class haconiwaError(Exception): pass
class ConfigError(haconiwaError): pass
class WorldError(haconiwaError): pass
class AgentError(haconiwaError): pass
class TaskError(haconiwaError): pass
```

## Command Structure

Built using Typer framework:
- Command groups implemented as Typer apps
- Subcommands use function decorators
- Type hints for argument validation
- Rich for terminal formatting
- Click for underlying CLI functionality

Example structure:
```python
app = typer.Typer()
core_app = typer.Typer()
app.add_typer(core_app, name="core")

@core_app.command()
def init(config: Path = None):
    """Initialize haconiwa environment"""
    pass
```

For detailed API documentation, see source code docstrings and type hints.