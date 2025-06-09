from importlib.metadata import version
from typing import Dict, Any

from .core.config import Config
from .core.logging import setup_logging
from .core.state import StateManager
from .world.provider.local import LocalProvider

try:
    from .world.provider.docker import DockerProvider
except ImportError:
    DockerProvider = None

from .agent.base import BaseAgent
from .agent.boss import BossAgent
from .agent.worker import WorkerAgent
from .agent.manager import AgentManager
from .task.worktree import WorktreeManager
from .watch.monitor import Monitor

__version__ = version("haconiwa")

DEFAULT_CONFIG: Dict[str, Any] = {
    "log_level": "INFO",
    "data_dir": "~/.haconiwa",
    "world": {
        "default_provider": "local",
        "providers": {
            "local": {"class": "LocalProvider"},
            "docker": {"class": "DockerProvider"}
        }
    },
    "agent": {
        "types": {
            "boss": {"class": "BossAgent"},
            "worker": {"class": "WorkerAgent"},
            "manager": {"class": "AgentManager"}
        }
    }
}

def initialize() -> None:
    """Initialize haconiwa with default configuration."""
    setup_logging("INFO")

__all__ = [
    "Config",
    "StateManager",
    "LocalProvider",
]

if DockerProvider:
    __all__.append("DockerProvider")

__all__.extend([
    "BaseAgent",
    "BossAgent", 
    "WorkerAgent",
    "AgentManager",
    "WorktreeManager",
    "Monitor",
    "initialize",
    "__version__"
])