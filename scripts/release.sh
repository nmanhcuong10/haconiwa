#!/bin/bash

set -e

# バージョン番号の更新確認
VERSION=$(python -c "import toml; print(toml.load('src/pyproject.toml')['tool']['poetry']['version'])")
echo "Current version: $VERSION"

# テストスイートの実行
pytest

# パッケージビルド
python -m build

# twine による PyPI アップロード
twine upload dist/*

# Git タグの作成とプッシュ
git tag "v$VERSION"
git push origin "v$VERSION"

# GitHub リリースの作成
gh release create "v$VERSION" --title "Release $VERSION" --notes "Release notes for version $VERSION" dist/*

# リリースノートの生成
echo "Release $VERSION has been created successfully."