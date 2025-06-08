# test/__init__.py

import pytest

# テスト設定の定義
pytest_plugins = ["pytest_asyncio"]

# Pythonテストランナーとの統合設定
def pytest_configure():
    # ここに設定を追加
    pass;