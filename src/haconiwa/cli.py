import typer
from typing import Optional, List
from pathlib import Path
import logging
import sys
import yaml

from haconiwa.core.cli import core_app
from haconiwa.world.cli import world_app
from haconiwa.space.cli import company_app as original_company_app
from haconiwa.resource.cli import resource_app as original_resource_app
from haconiwa.agent.cli import agent_app
from haconiwa.task.cli import task_app
from haconiwa.watch.cli import watch_app

# Import new v1.0 components
from haconiwa.core.crd.parser import CRDParser, CRDValidationError
from haconiwa.core.applier import CRDApplier
from haconiwa.core.policy.engine import PolicyEngine
from haconiwa.space.manager import SpaceManager

app = typer.Typer(
    name="haconiwa",
    help="AI協調開発支援Python CLIツール v1.0 - 宣言型YAML + tmux + Git worktree",
    no_args_is_help=True
)

def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def version_callback(value: bool):
    if value:
        from haconiwa import __version__
        typer.echo(f"haconiwa version {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="詳細なログ出力を有効化"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="設定ファイルのパス"),
    version: bool = typer.Option(False, "--version", callback=version_callback, help="バージョン情報を表示"),
):
    """箱庭 (haconiwa) v1.0 - 宣言型YAML + tmux + Git worktreeフレームワーク"""
    setup_logging(verbose)
    if config:
        try:
            from haconiwa.core.config import load_config
            load_config(config)
        except Exception as e:
            typer.echo(f"設定ファイルの読み込みに失敗: {e}", err=True)
            sys.exit(1)

# =====================================================================
# v1.0 新コマンド
# =====================================================================

@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="既存設定を上書き")
):
    """Haconiwa設定を初期化"""
    config_dir = Path.home() / ".haconiwa"
    config_file = config_dir / "config.yaml"
    
    if config_file.exists() and not force:
        overwrite = typer.confirm("Configuration already exists. Overwrite?")
        if not overwrite:
            typer.echo("❌ Initialization cancelled")
            return
    
    # Create config directory
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create default configuration
    default_config = {
        "version": "v1",
        "default_base_path": "./workspaces",
        "tmux": {
            "default_session_prefix": "haconiwa",
            "default_layout": "tiled"
        },
        "policy": {
            "default_policy": "default-command-whitelist"
        }
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
    typer.echo(f"✅ Haconiwa configuration initialized at {config_file}")

@app.command()
def apply(
    file: str = typer.Option(..., "-f", "--file", help="YAML ファイルパス"),
    dry_run: bool = typer.Option(False, "--dry-run", help="適用をシミュレート"),
):
    """CRD定義ファイルを適用"""
    file_path = Path(file)
    
    if not file_path.exists():
        typer.echo(f"❌ File not found: {file}", err=True)
        raise typer.Exit(1)
    
    parser = CRDParser()
    applier = CRDApplier()
    
    if dry_run:
        typer.echo("🔍 Dry run mode - no changes will be applied")
    
    try:
        # Check if file contains multiple documents
        with open(file_path, 'r') as f:
            content = f.read()
        
        if '---' in content:
            # Multi-document YAML
            crds = parser.parse_multi_yaml(content)
            typer.echo(f"📄 Found {len(crds)} resources in {file}")
            
            if not dry_run:
                results = applier.apply_multiple(crds)
                success_count = sum(results)
                typer.echo(f"✅ Applied {success_count}/{len(crds)} resources successfully")
            else:
                for crd in crds:
                    typer.echo(f"  - {crd.kind}: {crd.metadata.name}")
        else:
            # Single document
            crd = parser.parse_file(file_path)
            typer.echo(f"📄 Found resource: {crd.kind}/{crd.metadata.name}")
            
            if not dry_run:
                success = applier.apply(crd)
                if success:
                    typer.echo("✅ Applied 1 resource successfully")
                else:
                    typer.echo("❌ Failed to apply resource", err=True)
                    raise typer.Exit(1)
    
    except CRDValidationError as e:
        typer.echo(f"❌ Validation error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)

# =====================================================================
# Space コマンド（company のリネーム・拡張）
# =====================================================================

space_app = typer.Typer(name="space", help="World/Company/Room/Desk 管理")

@space_app.command("ls")
def space_list():
    """Space一覧を表示"""
    space_manager = SpaceManager()
    spaces = space_manager.list_spaces()
    
    if not spaces:
        typer.echo("No active spaces found")
        return
    
    typer.echo("📋 Active Spaces:")
    for space in spaces:
        typer.echo(f"  🏢 {space['name']} - {space['status']} ({space['panes']} panes, {space['rooms']} rooms)")

@space_app.command("start")
def space_start(
    company: str = typer.Option(..., "-c", "--company", help="Company name")
):
    """Company セッションを開始"""
    space_manager = SpaceManager()
    success = space_manager.start_company(company)
    
    if success:
        typer.echo(f"✅ Started company: {company}")
    else:
        typer.echo(f"❌ Failed to start company: {company}", err=True)
        raise typer.Exit(1)

@space_app.command("stop")
def space_stop(
    company: str = typer.Option(..., "-c", "--company", help="Company name")
):
    """Company セッションを停止"""
    space_manager = SpaceManager()
    success = space_manager.cleanup_session(company)
    
    if success:
        typer.echo(f"✅ Stopped company: {company}")
    else:
        typer.echo(f"❌ Failed to stop company: {company}", err=True)
        raise typer.Exit(1)

@space_app.command("attach")
def space_attach(
    company: str = typer.Option(..., "-c", "--company", help="Company name"),
    room: str = typer.Option("room-01", "-r", "--room", help="Room ID")
):
    """特定のRoom に接続"""
    space_manager = SpaceManager()
    success = space_manager.attach_to_room(company, room)
    
    if success:
        typer.echo(f"✅ Attached to {company}/{room}")
    else:
        typer.echo(f"❌ Failed to attach to {company}/{room}", err=True)
        raise typer.Exit(1)

@space_app.command("clone")
def space_clone(
    company: str = typer.Option(..., "-c", "--company", help="Company name")
):
    """Git リポジトリをclone"""
    space_manager = SpaceManager()
    success = space_manager.clone_repository(company)
    
    if success:
        typer.echo(f"✅ Cloned repository for: {company}")
    else:
        typer.echo(f"❌ Failed to clone repository for: {company}", err=True)
        raise typer.Exit(1)

# =====================================================================
# Tool コマンド（resource のリネーム・拡張）
# =====================================================================

tool_app = typer.Typer(name="tool", help="ファイルスキャン・DB スキャン機能")

@tool_app.command()
def scan_filepath(
    pathscan: str = typer.Option(..., "--scan-filepath", help="PathScan CRD名"),
    yaml_output: bool = typer.Option(False, "--yaml", help="YAML形式で出力"),
    json_output: bool = typer.Option(False, "--json", help="JSON形式で出力")
):
    """ファイルパススキャンを実行"""
    # Mock implementation - would integrate with actual PathScanner
    typer.echo(f"🔍 Scanning files with PathScan: {pathscan}")
    
    # Simulate file scan results
    files = ["src/main.py", "src/utils.py", "src/config.py"]
    
    if yaml_output:
        typer.echo("files:")
        for file in files:
            typer.echo(f"  - {file}")
    elif json_output:
        import json
        typer.echo(json.dumps({"files": files}, indent=2))
    else:
        typer.echo("📁 Found files:")
        for file in files:
            typer.echo(f"  📄 {file}")

@tool_app.command()
def scan_db(
    database: str = typer.Option(..., "--scan-db", help="Database CRD名"),
    yaml_output: bool = typer.Option(False, "--yaml", help="YAML形式で出力"),
    json_output: bool = typer.Option(False, "--json", help="JSON形式で出力")
):
    """データベーススキャンを実行"""
    # Mock implementation - would integrate with actual DatabaseScanner
    typer.echo(f"🔍 Scanning database: {database}")
    
    # Simulate database scan results
    tables = ["users", "posts", "comments"]
    
    if yaml_output:
        typer.echo("tables:")
        for table in tables:
            typer.echo(f"  - {table}")
    elif json_output:
        import json
        typer.echo(json.dumps({"tables": tables}, indent=2))
    else:
        typer.echo("🗄️ Found tables:")
        for table in tables:
            typer.echo(f"  📋 {table}")

# =====================================================================
# Policy コマンド（新規）
# =====================================================================

policy_app = typer.Typer(name="policy", help="CommandPolicy 管理")

@policy_app.command("ls")
def policy_list():
    """Policy一覧を表示"""
    policy_engine = PolicyEngine()
    policies = policy_engine.list_policies()
    
    if not policies:
        typer.echo("No policies found")
        return
    
    typer.echo("🛡️ Available Policies:")
    for policy in policies:
        active_mark = "🟢" if policy.get("active", False) else "⚪"
        typer.echo(f"  {active_mark} {policy['name']} ({policy['type']})")

@policy_app.command("test")
def policy_test(
    target: str = typer.Argument(..., help="Test target (agent)"),
    agent_id: str = typer.Argument(..., help="Agent ID"),
    cmd: str = typer.Option(..., "--cmd", help="Command to test")
):
    """コマンドがpolicyで許可されるかテスト"""
    if target != "agent":
        typer.echo("❌ Only 'agent' target is supported", err=True)
        raise typer.Exit(1)
    
    policy_engine = PolicyEngine()
    allowed = policy_engine.test_command(agent_id, cmd)
    
    if allowed:
        typer.echo(f"✅ Command allowed for agent {agent_id}: {cmd}")
    else:
        typer.echo(f"❌ Command denied for agent {agent_id}: {cmd}")

@policy_app.command("delete")
def policy_delete(
    name: str = typer.Argument(..., help="Policy name to delete")
):
    """Policy を削除"""
    policy_engine = PolicyEngine()
    success = policy_engine.delete_policy(name)
    
    if success:
        typer.echo(f"✅ Deleted policy: {name}")
    else:
        typer.echo(f"❌ Policy not found: {name}", err=True)
        raise typer.Exit(1)

# =====================================================================
# アプリケーション登録
# =====================================================================

# v1.0 新コマンド
app.add_typer(space_app, name="space")
app.add_typer(tool_app, name="tool")
app.add_typer(policy_app, name="policy")

# 既存コマンド（一部deprecated）
app.add_typer(core_app, name="core")
app.add_typer(world_app, name="world")
app.add_typer(agent_app, name="agent")
app.add_typer(task_app, name="task")
app.add_typer(watch_app, name="watch")

# 後方互換性のため残す（deprecation warning付き）
app.add_typer(original_company_app, name="company", deprecated=True)
app.add_typer(original_resource_app, name="resource", deprecated=True)

if __name__ == "__main__":
    app()