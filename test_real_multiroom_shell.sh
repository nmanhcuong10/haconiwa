#!/bin/bash
set -e  # エラーで停止

# マルチルーム機能の実際のテストスクリプト
# Real multiroom function test using shell script

# 引数解析
NON_INTERACTIVE=false
YAML_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--non-interactive)
            NON_INTERACTIVE=true
            shift
            ;;
        -f|--file)
            YAML_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -f, --file FILE         Specify YAML file to use (default: multiroom-test.yaml)"
            echo "  -n, --non-interactive   Run in non-interactive mode (skip manual inspection)"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Interactive mode with default YAML"
            echo "  $0 -f custom-test.yaml               # Use custom YAML file"
            echo "  $0 --non-interactive                 # Automated testing mode"
            echo "  $0 -f multiroom-test.yaml -n         # Custom YAML + non-interactive"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# デフォルトYAMLファイル設定
if [[ -z "$YAML_FILE" ]]; then
    YAML_FILE="multiroom-test.yaml"
fi

echo "🚀 Haconiwa Multiroom Function - Real Shell Test"
echo "================================================="

if [[ "$NON_INTERACTIVE" == true ]]; then
    echo "🤖 Running in non-interactive mode"
fi

echo "📝 Using YAML file: $YAML_FILE"

# カラー設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# テスト設定（YAMLファイルから会社名を抽出）
if [[ ! -f "$YAML_FILE" ]]; then
    echo -e "${RED}❌ YAML file not found: $YAML_FILE${NC}"
    echo "Please create the YAML file or specify a different file with -f option"
    exit 1
fi

# YAMLから会社名を抽出
TEST_SESSION=$(grep -A 20 "companies:" "$YAML_FILE" | grep "name:" | head -1 | sed 's/.*name: *//g' | tr -d '"')
if [[ -z "$TEST_SESSION" ]]; then
    echo -e "${RED}❌ Cannot extract company name from YAML file${NC}"
    exit 1
fi

TEST_DIR="/tmp/haconiwa-shell-test"

echo "🏢 Test session name: $TEST_SESSION"

# ヘルパー関数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# クリーンアップ関数
cleanup() {
    log_info "Cleaning up test environment..."
    
    # tmuxセッション削除
    if tmux has-session -t "$TEST_SESSION" 2>/dev/null; then
        tmux kill-session -t "$TEST_SESSION"
        log_info "Killed tmux session: $TEST_SESSION"
    fi
    
    # テストディレクトリ削除
    if [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
        log_info "Removed test directory: $TEST_DIR"
    fi
    
    # ローカルテストディレクトリも削除
    if [ -d "./test-multiroom-desks" ]; then
        rm -rf "./test-multiroom-desks"
        log_info "Removed local test directory: ./test-multiroom-desks"
    fi
}

# SIGINT/SIGTERM処理
trap cleanup EXIT

# Step 1: テスト環境準備
log_info "Step 1: Preparing test environment..."

# 既存のクリーンアップ
cleanup

# テストディレクトリ作成
mkdir -p "$TEST_DIR"
log_success "Created test directory: $TEST_DIR"

# Step 2: YAMLファイル確認
log_info "Step 2: Validating YAML file..."

log_success "Found YAML file: $YAML_FILE"

# YAML内容表示
log_info "YAML content preview:"
head -20 "$YAML_FILE"
echo "..."

# Step 3: haconiwa apply実行
log_info "Step 3: Running haconiwa apply command..."

echo "🎯 Executing: haconiwa apply -f $YAML_FILE"

if haconiwa apply -f "$YAML_FILE"; then
    log_success "haconiwa apply command succeeded"
else
    log_error "haconiwa apply command failed"
    exit 1
fi

# Step 4: tmuxセッション確認
log_info "Step 4: Checking tmux session..."

sleep 2  # セッション作成待ち

if tmux has-session -t "$TEST_SESSION" 2>/dev/null; then
    log_success "tmux session found: $TEST_SESSION"
else
    log_error "tmux session not found: $TEST_SESSION"
    exit 1
fi

# Step 5: ウィンドウ構造確認
log_info "Step 5: Verifying window structure..."

echo "📊 tmux session structure:"
echo "Session: $TEST_SESSION"

# ウィンドウ一覧取得
WINDOWS=$(tmux list-windows -t "$TEST_SESSION" -F "#{window_index}:#{window_name}")
WINDOW_COUNT=$(echo "$WINDOWS" | wc -l)

echo "Total windows: $WINDOW_COUNT"

if [ "$WINDOW_COUNT" -eq 2 ]; then
    log_success "Correct number of windows (2)"
else
    log_warning "Expected 2 windows, got $WINDOW_COUNT"
fi

# 各ウィンドウの詳細
echo "$WINDOWS" | while IFS=':' read -r window_id window_name; do
    echo "├── Window $window_id: $window_name"
    
    # ペイン数確認
    PANE_COUNT=$(tmux list-panes -t "$TEST_SESSION:$window_id" | wc -l)
    echo "│   └── Panes: $PANE_COUNT"
    
    # 最初の4ペインのタイトル表示
    echo "│       Sample pane titles:"
    tmux list-panes -t "$TEST_SESSION:$window_id" -F "#{pane_index}:#{pane_title}" | head -4 | while IFS=':' read -r pane_index pane_title; do
        echo "│       ├── Pane $pane_index: $pane_title"
    done
    
    if [ "$PANE_COUNT" -gt 4 ]; then
        echo "│       └── ... and $(($PANE_COUNT - 4)) more panes"
    fi
done

# Step 6: ディレクトリ構造確認
log_info "Step 6: Checking directory structure..."

# YAMLファイルからbasePath抽出
COMPANY_DIR=$(grep -A 10 "basePath:" "$YAML_FILE" | head -1 | sed 's/.*basePath: *//g')
if [[ -z "$COMPANY_DIR" ]]; then
    COMPANY_DIR="./test-multiroom-desks"  # デフォルト
fi

if [ -d "$COMPANY_DIR" ]; then
    log_success "Company directory created: $COMPANY_DIR"
    
    echo "📁 Directory structure:"
    if command -v tree >/dev/null 2>&1; then
        tree "$COMPANY_DIR" -L 2
    else
        find "$COMPANY_DIR" -type d | head -10 | sed 's/^/  /'
    fi
else
    log_warning "Company directory not found: $COMPANY_DIR"
fi

# Step 7: ルーム切り替えテスト
log_info "Step 7: Testing room switching functionality..."

echo "🔄 Testing room switching..."

# Alpha Room (Window 0)に切り替え
log_info "Switching to Alpha Room (Window 0)..."
if tmux select-window -t "$TEST_SESSION:0"; then
    CURRENT_WINDOW=$(tmux display-message -t "$TEST_SESSION" -p "#{window_index}")
    if [ "$CURRENT_WINDOW" = "0" ]; then
        log_success "Successfully switched to Alpha Room"
    else
        log_warning "Window switch may have failed"
    fi
else
    log_error "Failed to switch to Alpha Room"
fi

# Beta Room (Window 1)に切り替え
log_info "Switching to Beta Room (Window 1)..."
if tmux select-window -t "$TEST_SESSION:1"; then
    CURRENT_WINDOW=$(tmux display-message -t "$TEST_SESSION" -p "#{window_index}")
    if [ "$CURRENT_WINDOW" = "1" ]; then
        log_success "Successfully switched to Beta Room"
    else
        log_warning "Window switch may have failed"
    fi
else
    log_error "Failed to switch to Beta Room"
fi

# Step 8: 実際のペイン操作テスト
log_info "Step 8: Testing actual pane operations..."

echo "🖥️  Testing pane operations..."

# 最初のペインでコマンド実行
log_info "Sending command to first pane..."
tmux send-keys -t "$TEST_SESSION:0.0" "pwd" Enter
sleep 1

# ペインの現在パス確認
PANE_PATH=$(tmux display-message -t "$TEST_SESSION:0.0" -p "#{pane_current_path}")
echo "First pane current path: $PANE_PATH"

if [[ "$PANE_PATH" == *"org-01"* ]]; then
    log_success "Pane is in correct organization directory"
else
    log_warning "Pane path may not be as expected"
fi

# Step 9: 結果サマリー
log_info "Step 9: Test results summary..."

echo ""
echo "================================================="
echo "🎯 SHELL TEST RESULTS SUMMARY"
echo "================================================="

# 基本チェック
BASIC_CHECKS=0
TOTAL_CHECKS=4

# 1. Session existence
if tmux has-session -t "$TEST_SESSION" 2>/dev/null; then
    log_success "Session Creation: PASS"
    BASIC_CHECKS=$((BASIC_CHECKS + 1))
else
    log_error "Session Creation: FAIL"
fi

# 2. Window count
WINDOW_COUNT=$(tmux list-windows -t "$TEST_SESSION" | wc -l)
if [ "$WINDOW_COUNT" -eq 2 ]; then
    log_success "Window Count (2): PASS"
    BASIC_CHECKS=$((BASIC_CHECKS + 1))
else
    log_error "Window Count: FAIL (expected 2, got $WINDOW_COUNT)"
fi

# 3. Directory structure
if [ -d "$COMPANY_DIR" ]; then
    log_success "Directory Structure: PASS"
    BASIC_CHECKS=$((BASIC_CHECKS + 1))
else
    log_error "Directory Structure: FAIL"
fi

# 4. Room switching
if tmux select-window -t "$TEST_SESSION:0" && tmux select-window -t "$TEST_SESSION:1"; then
    log_success "Room Switching: PASS"
    BASIC_CHECKS=$((BASIC_CHECKS + 1))
else
    log_error "Room Switching: FAIL"
fi

echo ""
echo "📊 Test Score: $BASIC_CHECKS/$TOTAL_CHECKS"
echo "📝 YAML file used: $YAML_FILE"

if [ "$BASIC_CHECKS" -eq "$TOTAL_CHECKS" ]; then
    log_success "🎉 ALL TESTS PASSED! Multiroom function is working correctly."
    echo ""
    echo "🏗️  Summary of created structure:"
    echo "   └── Session: $TEST_SESSION"
    echo "       ├── Window 0: Alpha Development Room"
    echo "       └── Window 1: Beta Testing Room"
    echo ""
    echo "🔧 You can now attach to the session with:"
    echo "   tmux attach-session -t $TEST_SESSION"
    echo ""
    EXIT_CODE=0
else
    log_error "Some tests failed. Multiroom function needs attention."
    EXIT_CODE=1
fi

# Step 10: 手動確認オプション（非対話モードでは自動スキップ）
if [[ "$NON_INTERACTIVE" == false ]]; then
    echo ""
    read -p "🤔 Do you want to attach to the session for manual inspection? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Attaching to session $TEST_SESSION..."
        log_info "Use Ctrl+b, 0/1 to switch between Alpha/Beta rooms"
        log_info "Use Ctrl+b, d to detach from session"
        echo ""
        tmux attach-session -t "$TEST_SESSION"
    fi
else
    log_info "Non-interactive mode: Skipping manual inspection"
fi

echo ""
log_info "Test completed. Session will be cleaned up on exit."

exit $EXIT_CODE 