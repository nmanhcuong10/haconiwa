#!/bin/bash

# Python 仮想環境の作成と有効化
python3 -m venv .venv
source .venv/bin/activate

# 依存関係の一括インストール
pip install -e .[dev]

# pre-commit フックの設定
pre-commit install

# tmux, git の設定確認
tmux -V
git --version

# 初期設定ファイルの生成
if [ ! -f config.yaml ]; then
    echo "初期設定ファイルを生成します..."
    touch config.yaml
fi

# 開発用データベースのセットアップ
if [ ! -d db ]; then
    mkdir db
    echo "データベースのセットアップが完了しました。"
fi

# 開発サーバーの起動確認
echo "開発サーバーを起動します..."
# ここにサーバー起動コマンドを追加 (例: python -m flask run)