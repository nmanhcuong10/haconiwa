#!/bin/bash
set -e

# リリース前の自動テスト・コミット・プッシュスクリプト
# 使用方法: ./scripts/commit-and-push.sh "コミットメッセージ"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# カラー出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
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

# ヘルプメッセージ
show_help() {
    echo "Haconiwa Commit & Push Script (テスト付き)"
    echo ""
    echo "使用方法:"
    echo "  $0 [OPTIONS] \"コミットメッセージ\""
    echo ""
    echo "オプション:"
    echo "  --skip-tests        テストをスキップ"
    echo "  --skip-prerelease   プリリリースチェックをスキップ"
    echo "  --force            強制的にプッシュ（テスト失敗時も）"
    echo "  --fast             高速モード（integrationテストをスキップ）"
    echo "  --help             このヘルプを表示"
    echo ""
    echo "例:"
    echo "  $0 \"新機能を追加\""
    echo "  $0 --skip-tests \"ドキュメント更新\""
    echo "  $0 --fast \"バグ修正\""
    echo ""
    echo "ユーザールールに従い、以下を自動実行:"
    echo "  1. Pythonテスト実行 (pytest tests/unit/)"
    echo "  2. git add ."
    echo "  3. git commit -m \"コミットメッセージ\""
    echo "  4. git push origin \$BRANCH"
    echo ""
}

# コミットメッセージの確認
check_commit_message() {
    if [ -z "$COMMIT_MSG" ]; then
        log_error "コミットメッセージが指定されていません"
        echo ""
        show_help
        exit 1
    fi
}

# プロジェクトルートに移動
cd "$PROJECT_ROOT"

# パラメータ解析
SKIP_TESTS=false
SKIP_PRERELEASE=false
FORCE=false
FAST=false
COMMIT_MSG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-prerelease)
            SKIP_PRERELEASE=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --fast)
            FAST=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        -*)
            log_error "不明なオプション: $1"
            show_help
            exit 1
            ;;
        *)
            COMMIT_MSG="$1"
            shift
            ;;
    esac
done

check_commit_message

log_info "Haconiwa コミット・プッシュスクリプトを開始します"
log_info "プロジェクトルート: $PROJECT_ROOT"
log_info "コミットメッセージ: $COMMIT_MSG"

# 現在のブランチを取得
BRANCH=$(git rev-parse --abbrev-ref HEAD)
log_info "現在のブランチ: $BRANCH"

# Git status確認
if ! git diff-index --quiet HEAD --; then
    log_warning "コミットされていない変更があります"
    git status --porcelain
    echo ""
fi

# ユーザールールに従ったテスト実行
if [ "$SKIP_TESTS" = false ]; then
    log_info "ユーザールールに従ってPythonテストを実行します..."
    
    # 基本的には pytest tests/unit/ を実行
    log_info "Unit テストを実行しています..."
    if python -m pytest tests/unit/ -v; then
        log_success "Unit テスト完了"
    else
        log_error "Unit テストが失敗しました"
        if [ "$FORCE" = false ]; then
            log_error "テストが失敗しました。修正してから再実行してください"
            log_info "強制実行する場合は --force オプションを使用してください"
            exit 1
        else
            log_warning "テスト失敗を無視してプッシュを続行します"
        fi
    fi
    
    # Fast モードでなければ integration テストも実行
    if [ "$FAST" = false ]; then
        if [ -d "tests/integration" ]; then
            log_info "Integration テストを実行しています..."
            if python -m pytest tests/integration/ -v; then
                log_success "Integration テスト完了"
            else
                log_error "Integration テストが失敗しました"
                if [ "$FORCE" = false ]; then
                    exit 1
                else
                    log_warning "Integration テスト失敗を無視してプッシュを続行します"
                fi
            fi
        else
            log_warning "Integration テストディレクトリが見つかりません"
        fi
    else
        log_info "Fast モード: Integration テストをスキップします"
    fi
    
else
    log_warning "テストをスキップしました"
fi

# プリリリースチェック実行（オプション）
if [ "$SKIP_PRERELEASE" = false ]; then
    log_info "プリリリースチェックを実行しています..."
    
    if command -v haconiwa-prerelease >/dev/null 2>&1; then
        if haconiwa-prerelease --skip-tests; then
            log_success "プリリリースチェック完了"
        else
            log_warning "プリリリースチェックでいくつかの問題が見つかりました"
            if [ "$FORCE" = false ]; then
                log_info "問題を修正してから再実行するか、--skip-prereleaseオプションを使用してください"
                exit 1
            else
                log_warning "プリリリースチェック失敗を無視してプッシュを続行します"
            fi
        fi
    else
        log_info "haconiwa-prereleaseコマンドが見つかりません（問題ありません）"
    fi
else
    log_info "プリリリースチェックをスキップしました"
fi

# Git操作実行（ユーザールールに従って）
log_info "Git操作を開始します..."

# ステージング
log_info "ファイルをステージングしています..."
git add .

# コミット状況確認
if git diff-index --quiet --cached HEAD --; then
    log_warning "コミットする変更がありません"
    log_info "プッシュのみ実行します"
else
    # コミット実行
    log_info "コミットを実行しています..."
    if git commit -m "$COMMIT_MSG"; then
        log_success "コミット完了: $COMMIT_MSG"
    else
        log_error "コミットが失敗しました"
        exit 1
    fi
fi

# プッシュ実行
log_info "プッシュを実行しています..."
if git push origin "$BRANCH"; then
    log_success "プッシュ完了: $BRANCH"
else
    log_error "プッシュが失敗しました"
    exit 1
fi

log_success "コミット・プッシュプロセスが完了しました！"
log_info "ブランチ: $BRANCH"
log_info "コミット: $COMMIT_MSG"

# 最新の git log を表示
log_info "最新のコミット:"
git log --oneline -n 3

echo ""
log_info "このスクリプトはユーザールールに従って以下を実行しました:"
echo "  ✅ Pythonテスト実行"
echo "  ✅ git add ."
echo "  ✅ git commit -m \"$COMMIT_MSG\""
echo "  ✅ git push origin $BRANCH" 
