# src/haconiwa/core/__init__.py

"""
Haconiwa Core Module
"""

from .config import Config
from .state import StateManager

# v1.0 新機能
try:
    from .crd import *
    from .applier import CRDApplier
    from .policy import *
except ImportError:
    # v1.0機能がない場合はスキップ
    pass

__all__ = [
    'Config',
    'StateManager'
]