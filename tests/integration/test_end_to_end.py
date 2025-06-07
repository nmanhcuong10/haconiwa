import pytest
import subprocess
import os
import shutil
import time
import yaml
from pathlib import Path

# テスト用の設定ファイルやディレクトリのパス
TEST_DIR = Path(__file__).parent
haconiwa_ROOT = TEST_DIR.parent.parent.parent # プロジェクトルートを想定
TEST_CONFIG_DIR = TEST_DIR / "test_config"
TEST_haconiwa_DIR = TEST_DIR / ".haconiwa_test"

@pytest.fixture(scope="function")
def setup_haconiwa_env():
    """テストごとに一時的なhaconiwa環境をセットアップ・クリーンアップするフィクスチャ"""
    # テスト用ディレクトリを作成
    if TEST_haconiwa_DIR.exists():
        shutil.rmtree(TEST_haconiwa_DIR)
    TEST_haconiwa_DIR.mkdir()

    # 環境変数でhaconiwaのルートディレクトリを指定
    os.environ["haconiwa_ROOT"] = str(TEST_haconiwa_DIR)

    yield TEST_haconiwa_DIR

    # クリーンアップ
    if TEST_haconiwa_DIR.exists():
        shutil.rmtree(TEST_HONIWA_DIR)
    if "haconiwa_ROOT" in os.environ:
        del os.environ["haconiwa_ROOT"]

def run_haconiwa_command(command, cwd=None):
    """haconiwa CLIコマンドを実行するヘルパー関数"""
    # CLIエントリーポイントを直接実行する代わりに、インストールされたコマンドを想定
    # または、開発モードでモジュールとして実行
    # ここでは簡単のため、subprocessで'haconiwa'コマンドを呼び出すことを想定
    # 実際のテストでは、pyproject.tomlの[project.scripts]を参考に実行方法を調整
    cmd = ["haconiwa"] + command
    print(f"\nRunning command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True, # 終了コードが0以外の場合は例外発生
            cwd=cwd
        )
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)
        pytest.fail(f"Command failed: {' '.join(cmd)}\n{e.stderr}")
    except FileNotFoundError:
        pytest.fail("haconiwa command not found. Ensure it's installed or in PATH.")


def test_e2e_basic_workflow(setup_haconiwa_env):
    """
    基本的なhaconiwaワークフローのエンドツーエンドテスト
    (init -> world create -> space create -> agent spawn -> task new)
    """
    haconiwa_root = setup_haconiwa_env
    print(f"Using haconiwa root: {haconiwa_root}")

    # 1. core init
    print("Testing: haconiwa core init")
    run_haconiwa_command(["core", "init"])
    assert (haconiwa_root / "config.yaml").exists()
    assert (haconiwa_root / "state.json").exists() # state.pyがjson/pickleを使うと想定
    assert (haconiwa_root / "organizations").exists()
    assert (haconiwa_root / "worlds").exists()

    # 2. world create
    print("Testing: haconiwa world create local-dev")
    world_name = "local-dev"
    run_haconiwa_command(["world", "create", world_name, "--provider", "local"])
    world_config_path = haconiwa_root / "worlds" / f"{world_name}.yaml"
    assert world_config_path.exists()
    # world configの内容を検証 (スタブ)
    with open(world_config_path, 'r') as f:
        world_config = yaml.safe_load(f)
        assert world_config.get("world_id") == world_name
        assert world_config.get("provider") == "local"

    # 3. space create (world内で実行を想定)
    # 実際のtmux操作はモック化またはテスト環境でのtmuxセットアップが必要
    # ここではCLIコマンドがエラーなく実行されるかを確認するスタブ
    print("Testing: haconiwa space create (within world)")
    # 実際にはworldに入ってから実行するが、E2Eテストでは簡略化
    # run_haconiwa_command(["world", "enter", world_name]) # このコマンド自体はテスト済みとして
    # run_haconiwa_command(["space", "create", "dev-space"]) # world内で実行されるコマンド
    # 一時的にworldディレクトリをカレントディレクトリとしてコマンドを実行するシミュレーション
    world_dir = haconiwa_root / "worlds" # 実際にはworldの作業ディレクトリ
    # 実際にはworld create時に作業ディレクトリが作られる想定だが、ここでは簡略化
    (haconiwa_root / "worlds" / world_name).mkdir(exist_ok=True)
    run_haconiwa_command(["space", "create", "dev-space"], cwd=haconiwa_root / "worlds" / world_name)
    # tmuxセッションが作成されたかどうかの検証は外部依存のためスキップまたはモック

    # 4. agent spawn (組織設定が必要)
    # 組織設定ファイルを作成 (スタブ)
    org_id = "org-01"
    org_dir = haconiwa_root / "organizations" / org_id
    org_dir.mkdir(parents=True, exist_ok=True)
    org_config_content = """
organization_id: org-01
boss:
  model: dummy-boss-model
workers:
  - id: worker-a
    type: frontend
    model: dummy-worker-model
"""
    org_config_path = org_dir / "config.yaml"
    with open(org_config_path, "w") as f:
        f.write(org_config_content)

    print("Testing: haconiwa agent spawn boss org-01")
    # 実際にはworld内で実行される可能性もある
    run_haconiwa_command(["agent", "spawn", "boss", org_id])
    # エージェントが起動したかどうかの検証は複雑なためスキップまたはモック

    print("Testing: haconiwa agent spawn worker org-01 worker-a")
    run_haconiwa_command(["agent", "spawn", "worker", org_id, "worker-a"])
    # エージェントが起動したかどうかの検証は複雑なためスキップまたはモック

    # 5. task new (gitリポジトリが必要)
    # ダミーのgitリポジトリを作成 (スタブ)
    repo_dir = haconiwa_root / "dummy_repo"
    repo_dir.mkdir(exist_ok=True)
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    (repo_dir / "README.md").write_text("Dummy repo")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True)

    print("Testing: haconiwa task new")
    task_title = "Implement user login"
    # 実際にはリポジトリのルートなどで実行される可能性
    run_haconiwa_command(["task", "new", task_title, "--repo", str(repo_dir)], cwd=haconiwa_root)
    # worktreeが作成されたかどうかの検証 (スタブ)
    # git worktree list コマンドなどで検証可能だが、ここではファイル存在チェックで代用
    # worktreeは通常、リポジトリの親ディレクトリに作成されることが多い
    # 例: repo_dir/../.git/worktrees/...
    # 簡略化のため、特定のファイルが作成されたかチェックするスタブ
    # assert (repo_dir.parent / ".git" / "worktrees").exists() # 実際のgit構造に依存

    # 6. watch start (監視デーモン起動)
    print("Testing: haconiwa watch start")
    # 監視デーモンはバックグラウンドで起動することが多い
    # E2Eテストでは、デーモンが起動したことを確認し、必要なら停止する
    # ここではコマンドがエラーなく実行されるかを確認するスタブ
    # run_haconiwa_command(["watch", "start"])
    # 監視プロセスが起動したかどうかの検証は外部依存のためスキップまたはモック
    # time.sleep(1) # 起動を待つ
    # run_haconiwa_command(["watch", "stop"]) # クリーンアップ

    print("Basic workflow test completed successfully.")

# 他のE2Eテストケース (スタブ)
# def test_e2e_multiple_agents_coordination(setup_haconiwa_env):
#     """複数エージェント協調動作のテスト (スタブ)"""
#     haconiwa_root = setup_haconiwa_env
#     print("Testing: Multiple agents coordination (stub)")
#     # Boss, Worker A, Worker B を起動し、タスクを割り当て、協調して完了するシナリオをシミュレーション
#     # 複雑なエージェント間通信やタスク実行ロジックの検証が必要
#     pass

# def test_e2e_failure_recovery(setup_haconiwa_env):
#     """障害シナリオ・復旧のテスト (スタブ)"""
#     haconiwa_root = setup_haconiwa_env
#     print("Testing: Failure recovery (stub)")
#     # エージェントやworldを強制終了させ、haconiwaが状態を復旧できるかテスト
#     pass

# def test_e2e_performance_load(setup_haconiwa_env):
#     """パフォーマンス・負荷テスト (スタブ)"""
#     haconiwa_root = setup_haconiwa_env
#     print("Testing: Performance and load (stub)")
#     # 大量のタスクやエージェントを同時に実行し、システムの応答性やリソース使用率を測定
#     pass

# def test_e2e_security_integration(setup_haconiwa_env):
#     """セキュリティ統合テスト (スタブ)"""
#     haconiwa_root = setup_haconiwa_env
#     print("Testing: Security integration (stub)")
#     # 権限分離、namespace分離、設定ファイルのアクセス制御などが正しく機能するかテスト
#     pass