#!/bin/bash

set -e

# 色の定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_step() {
    echo -e "${BLUE}===> $1${NC}"
    sleep 1
}

cleanup() {
    echo_step "クリーンアップを実行中..."
    haconiwa watch stop
    haconiwa agent stop --all
    haconiwa world destroy local-dev
}

trap cleanup EXIT

# 初期化
echo_step "箱庭環境を初期化中..."
haconiwa core init

# 開発環境の作成
echo_step "開発用ワールドを作成中..."
haconiwa world create local-dev

# tmux区画の設定
echo_step "作業スペースを構築中..."
haconiwa space create --layout=dev

# AIエージェントの起動
echo_step "AIエージェントを起動中..."
haconiwa agent spawn boss --name main-boss
haconiwa agent spawn worker --name frontend-worker --type frontend
haconiwa agent spawn worker --name backend-worker --type backend
haconiwa agent spawn worker --name qa-worker --type qa

# タスクの作成と割り当て
echo_step "タスクを作成・割り当て中..."
TASK_ID=$(haconiwa task new --title "新機能実装" --description "ログイン機能の実装" --output=id)
haconiwa task assign $TASK_ID --to frontend-worker

# 監視の開始
echo_step "システム監視を開始中..."
haconiwa watch start --metrics=all

# 開発作業のシミュレーション
echo_step "開発作業をシミュレート中..."
sleep 5

echo -e "${GREEN}フロントエンドワーカーがタスクを実行中...${NC}"
sleep 3

echo -e "${GREEN}QAワーカーがテストを実行中...${NC}"
sleep 3

echo -e "${GREEN}タスクが完了しました${NC}"
haconiwa task done $TASK_ID

echo_step "デモが完了しました"