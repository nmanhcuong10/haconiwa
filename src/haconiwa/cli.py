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
    force_clone: bool = typer.Option(False, "--force-clone", help="既存ディレクトリを確認なしで削除してGitクローン"),
    attach: bool = typer.Option(False, "--attach", help="適用後に自動でセッションにアタッチ"),
    no_attach: bool = typer.Option(False, "--no-attach", help="適用後にセッションにアタッチしない（明示的指定）"),
    room: str = typer.Option("room-01", "-r", "--room", help="アタッチするルーム（--attachと併用）"),
):
    """CRD定義ファイルを適用"""
    file_path = Path(file)
    
    if not file_path.exists():
        typer.echo(f"❌ File not found: {file}", err=True)
        raise typer.Exit(1)
    
    # Handle attach/no-attach logic
    if attach and no_attach:
        typer.echo("❌ Cannot specify both --attach and --no-attach", err=True)
        raise typer.Exit(1)
    
    # Set final attach behavior
    should_attach = attach and not no_attach
    
    parser = CRDParser()
    applier = CRDApplier()
    
    # Set force_clone flag in applier
    applier.force_clone = force_clone
    
    if dry_run:
        typer.echo("🔍 Dry run mode - no changes will be applied")
        if should_attach:
            typer.echo(f"🔗 Would attach to session after apply (room: {room})")
    
    created_sessions = []  # Track created sessions for attach
    
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
                
                # Extract session names from applied Space CRDs
                for i, (crd, result) in enumerate(zip(crds, results)):
                    if result and crd.kind == "Space":
                        session_name = crd.spec.nations[0].cities[0].villages[0].companies[0].name
                        created_sessions.append(session_name)
            else:
                for crd in crds:
                    typer.echo(f"  - {crd.kind}: {crd.metadata.name}")
                    if crd.kind == "Space":
                        session_name = crd.spec.nations[0].cities[0].villages[0].companies[0].name
                        created_sessions.append(session_name)
        else:
            # Single document
            crd = parser.parse_file(file_path)
            typer.echo(f"📄 Found resource: {crd.kind}/{crd.metadata.name}")
            
            if not dry_run:
                success = applier.apply(crd)
                if success:
                    typer.echo("✅ Applied 1 resource successfully")
                    
                    # Extract session name for Space CRD
                    if crd.kind == "Space":
                        session_name = crd.spec.nations[0].cities[0].villages[0].companies[0].name
                        created_sessions.append(session_name)
                else:
                    typer.echo("❌ Failed to apply resource", err=True)
                    raise typer.Exit(1)
            else:
                if crd.kind == "Space":
                    session_name = crd.spec.nations[0].cities[0].villages[0].companies[0].name
                    created_sessions.append(session_name)
        
        # Auto-attach to session if requested
        if should_attach and created_sessions and not dry_run:
            session_name = created_sessions[0]  # Attach to first created session
            typer.echo(f"\n🔗 Auto-attaching to session: {session_name} (room: {room})")
            
            # Import subprocess for tmux attach
            import subprocess
            import os
            
            try:
                # Check if session exists
                result = subprocess.run(['tmux', 'has-session', '-t', session_name], 
                                       capture_output=True, text=True)
                if result.returncode != 0:
                    typer.echo(f"❌ Session '{session_name}' not found for attach", err=True)
                    raise typer.Exit(1)
                
                # Switch to specific room first
                space_manager = SpaceManager()
                space_manager.switch_to_room(session_name, room)
                
                # Attach to session (this will transfer control to tmux)
                typer.echo(f"🚀 Attaching to {session_name}/{room}...")
                typer.echo("💡 Press Ctrl+B then D to detach from tmux session")
                
                # Use execvp to replace current process with tmux attach
                os.execvp('tmux', ['tmux', 'attach-session', '-t', session_name])
                
            except FileNotFoundError:
                typer.echo("❌ tmux is not installed or not found in PATH", err=True)
                raise typer.Exit(1)
            except Exception as e:
                typer.echo(f"❌ Failed to attach to session: {e}", err=True)
                raise typer.Exit(1)
        
        elif should_attach and not created_sessions:
            typer.echo("⚠️ No Space sessions created, cannot attach")
    
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

@space_app.command("list")
def space_list_alias():
    """Space一覧を表示 (lsのalias)"""
    space_list()

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

@space_app.command("run")
def space_run(
    company: str = typer.Option(..., "-c", "--company", help="Company name"),
    command: str = typer.Option(None, "--cmd", help="Command to run in all panes"),
    claude_code: bool = typer.Option(False, "--claude-code", help="Run 'claude' command in all panes"),
    room: str = typer.Option(None, "-r", "--room", help="Target specific room (default: all rooms)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be executed without running"),
    confirm: bool = typer.Option(True, "--confirm/--no-confirm", help="Ask for confirmation before execution")
):
    """全ペインまたは指定ルームでコマンドを実行"""
    
    # Determine command to run
    if claude_code:
        actual_command = "claude"
    elif command:
        actual_command = command
    else:
        typer.echo("❌ Either --cmd or --claude-code must be specified", err=True)
        raise typer.Exit(1)
    
    # Import subprocess for tmux interaction
    import subprocess
    
    # Check if session exists
    try:
        result = subprocess.run(['tmux', 'has-session', '-t', company], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            typer.echo(f"❌ Company session '{company}' not found", err=True)
            raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ tmux is not installed or not found in PATH", err=True)
        raise typer.Exit(1)
    
    # Get list of panes
    try:
        if room:
            # Get panes for specific room (window)
            space_manager = SpaceManager()
            window_id = space_manager._get_window_id_for_room(room)
            result = subprocess.run(['tmux', 'list-panes', '-t', f'{company}:{window_id}', '-F', 
                                   '#{window_index}:#{pane_index}'], 
                                   capture_output=True, text=True)
            target_desc = f"room {room} (window {window_id})"
        else:
            # Get all panes in session
            result = subprocess.run(['tmux', 'list-panes', '-t', company, '-F', 
                                   '#{window_index}:#{pane_index}', '-a'], 
                                   capture_output=True, text=True)
            target_desc = "all rooms"
        
        if result.returncode != 0:
            typer.echo(f"❌ Failed to get panes: {result.stderr}", err=True)
            raise typer.Exit(1)
        
        panes = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        if not panes:
            typer.echo(f"❌ No panes found in {target_desc}", err=True)
            raise typer.Exit(1)
        
        typer.echo(f"🎯 Target: {company} ({target_desc})")
        typer.echo(f"📊 Found {len(panes)} panes")
        typer.echo(f"🚀 Command: {actual_command}")
        
        if dry_run:
            typer.echo("\n🔍 Dry run - Commands that would be executed:")
            for i, pane in enumerate(panes[:5]):  # Show first 5
                typer.echo(f"  Pane {pane}: tmux send-keys -t {company}:{pane} '{actual_command}' Enter")
            if len(panes) > 5:
                typer.echo(f"  ... and {len(panes) - 5} more panes")
            return
        
        # Confirmation
        if confirm:
            confirm_msg = f"Execute '{actual_command}' in {len(panes)} panes of {company}?"
            if not typer.confirm(confirm_msg):
                typer.echo("❌ Operation cancelled")
                raise typer.Exit(0)
        
        # Execute command in all panes
        typer.echo(f"\n🚀 Executing '{actual_command}' in {len(panes)} panes...")
        
        failed_panes = []
        for i, pane in enumerate(panes):
            try:
                # Send command to pane
                cmd = ['tmux', 'send-keys', '-t', f'{company}:{pane}', actual_command, 'Enter']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    typer.echo(f"  ✅ Pane {pane}: Command sent")
                else:
                    typer.echo(f"  ❌ Pane {pane}: Failed - {result.stderr}")
                    failed_panes.append(pane)
                    
            except subprocess.TimeoutExpired:
                typer.echo(f"  ⏱️ Pane {pane}: Timeout")
                failed_panes.append(pane)
            except Exception as e:
                typer.echo(f"  ❌ Pane {pane}: Error - {e}")
                failed_panes.append(pane)
        
        # Summary
        success_count = len(panes) - len(failed_panes)
        typer.echo(f"\n📊 Execution completed: {success_count}/{len(panes)} panes successful")
        
        if failed_panes:
            typer.echo(f"❌ Failed panes: {', '.join(failed_panes)}")
            raise typer.Exit(1)
        else:
            typer.echo("✅ All panes executed successfully")
            
    except Exception as e:
        typer.echo(f"❌ Error executing command: {e}", err=True)
        raise typer.Exit(1)

@space_app.command("delete")
def space_delete(
    company: str = typer.Option(..., "-c", "--company", help="Company name"),
    clean_dirs: bool = typer.Option(False, "--clean-dirs", help="Remove related directories"),
    force: bool = typer.Option(False, "--force", help="Force delete without confirmation")
):
    """Company セッションとリソースを削除"""
    
    # Import subprocess for tmux interaction
    import subprocess
    import shutil
    
    # Check if session exists
    try:
        result = subprocess.run(['tmux', 'has-session', '-t', company], 
                               capture_output=True, text=True)
        session_exists = result.returncode == 0
    except FileNotFoundError:
        typer.echo("❌ tmux is not installed or not found in PATH", err=True)
        raise typer.Exit(1)
    
    if not session_exists:
        typer.echo(f"⚠️ Company session '{company}' not found")
        if not clean_dirs:
            typer.echo("💡 Use --clean-dirs to clean up directories anyway")
            return
    
    # Confirmation
    if not force:
        operations = []
        if session_exists:
            operations.append(f"Kill tmux session: {company}")
        if clean_dirs:
            operations.append(f"Remove directories: ./{company}")
        
        if operations:
            typer.echo("This will:")
            for op in operations:
                typer.echo(f"  - {op}")
            
            if not typer.confirm("Are you sure you want to proceed?"):
                typer.echo("❌ Operation cancelled")
                raise typer.Exit(0)
    
    try:
        # Kill tmux session
        if session_exists:
            result = subprocess.run(['tmux', 'kill-session', '-t', company], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                typer.echo(f"✅ Killed tmux session: {company}")
            else:
                typer.echo(f"❌ Failed to kill session: {result.stderr}", err=True)
        
        # Clean directories
        if clean_dirs:
            dirs_to_clean = [
                f"./{company}",
                f"./{company}-desks",
                f"./test-{company}",
                f"./test-{company}-desks"
            ]
            
            cleaned_dirs = []
            for dir_path in dirs_to_clean:
                if Path(dir_path).exists():
                    try:
                        shutil.rmtree(dir_path)
                        cleaned_dirs.append(dir_path)
                        typer.echo(f"✅ Removed directory: {dir_path}")
                    except Exception as e:
                        typer.echo(f"❌ Failed to remove {dir_path}: {e}", err=True)
            
            if cleaned_dirs:
                typer.echo(f"🗑️ Cleaned {len(cleaned_dirs)} directories")
            else:
                typer.echo("ℹ️ No directories found to clean")
        
        # Remove from SpaceManager tracking
        space_manager = SpaceManager()
        if hasattr(space_manager, 'active_sessions') and company in space_manager.active_sessions:
            del space_manager.active_sessions[company]
            typer.echo(f"✅ Removed from space tracking: {company}")
        
        typer.echo(f"✅ Successfully deleted company: {company}")
        
    except Exception as e:
        typer.echo(f"❌ Error during deletion: {e}", err=True)
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