#!/bin/bash

# Python コード品質チェック用シェルスクリプト

# black フォーマット実行
black .

# flake8 リンティング
flake8 .

# mypy 型チェック
mypy .

# bandit セキュリティスキャン
bandit -r .

# isort インポート整理
isort .

# pytest カバレッジ測定
pytest --cov=src --cov-report=html

# エラー集約とレポート出力
echo "コード品質チェックが完了しました。"