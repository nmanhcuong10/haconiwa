pip install haconiwa

# 初期化
haconiwa core init

# 設定確認
haconiwa core status

# ローカル開発環境の作成
haconiwa world create local-dev

# 環境に入る
haconiwa world enter local-dev

# tmuxセッションの作成
haconiwa space create dev-space

# レイアウトの設定
haconiwa space resize --layout=grid

# Bossエージェントの起動
haconiwa agent spawn boss-1 --type=boss

# Workerエージェントの起動
haconiwa agent spawn worker-a --type=worker --skill=frontend
haconiwa agent spawn worker-b --type=worker --skill=backend

# 新規タスクの作成
haconiwa task new "実装: ログイン機能"

# タスクの割り当て
haconiwa task assign TASK-001 worker-a

# 進捗確認
haconiwa task show TASK-001

# サンプルプロジェクトのクローン
git clone https://github.com/haconiwa/example-todo-app.git
cd example-todo-app

# haconiwa環境のセットアップ
haconiwa core init
haconiwa world create todo-dev
haconiwa space create todo-space

# AIエージェントによる開発支援
haconiwa agent spawn boss-1 --type=boss
haconiwa task new "タスク: TODOリスト表示機能の実装"

# セッション一覧の確認
haconiwa space list

# 強制終了と再作成
haconiwa space kill dev-space
haconiwa space create dev-space

# エージェントの状態確認
haconiwa agent ps

# エージェントの再起動
haconiwa agent stop worker-a
haconiwa agent spawn worker-a --type=worker

# worktreeの状態確認
haconiwa task prune --dry-run

# 孤立worktreeの削除
haconiwa task prune --force

from haconiwa.core import haconiwaCore
from haconiwa.agent import BossAgent, WorkerAgent

# haconiwaコアの初期化
core = haconiwaCore()
core.initialize()

# エージェントの設定
boss = BossAgent("boss-1")
worker = WorkerAgent("worker-a", skill="frontend")

# タスクの作成と割り当て
task = core.create_task("新機能の実装")
boss.assign_task(task, worker)

# 進捗監視
for status in worker.watch_progress():
    print(f"タスク進捗: {status.progress}%")

from haconiwa.agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        
    async def process_task(self, task):
        # タスク処理ロジックの実装
        result = await self.execute_custom_logic(task)
        return result

from haconiwa.core import hooks

@hooks.on_task_complete
def handle_task_complete(task):
    print(f"タスク完了: {task.id}")
    
@hooks.on_agent_error
def handle_agent_error(agent, error):
    print(f"エージェントエラー: {agent.name} - {error}");