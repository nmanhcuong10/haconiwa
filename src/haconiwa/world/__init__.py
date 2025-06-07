# haconiwa/world/__init__.py

from .provider import local, docker

__all__ = ["local", "docker"]

def initialize():
    # worldモジュールの初期化処理
    pass

initialize();