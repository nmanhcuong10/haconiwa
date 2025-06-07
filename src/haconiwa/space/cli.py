import typer
from typing import Optional, List
from pathlib import Path

from ..space.tmux import TmuxSession
from ..core.config import Config
from ..core.logging import get_logger

logger = get_logger(__name__)
space_app = typer.Typer(help="tmuxスペース・セッション管理 (開発中)")

@space_app.command()
def create(
    name: str = typer.Argument(..., help="Space name"),
    layout: str = typer.Option("even-horizontal", help="Initial layout (even-horizontal/even-vertical/main-horizontal/main-vertical)"),
    panes: int = typer.Option(2, help="Number of panes"),
):
    """Create a new tmux space with specified layout"""
    config = Config("config.yaml")
    tmux = TmuxSession(config)
    try:
        session = tmux.create_session(name)
        typer.echo(f"Created space '{name}' with {panes} panes using {layout} layout")
        return session
    except Exception as e:
        logger.error(f"Failed to create space: {e}")
        raise typer.Exit(1)

@space_app.command()
def multiagent(
    name: str = typer.Option("multiagent", "--name", "-n", help="Session name"),
    base_path: str = typer.Option(".", "--base-path", "-p", help="Base path for workspaces"),
    org01_name: str = typer.Option("動画モデル", "--org01", help="Organization 1 name"),
    org02_name: str = typer.Option("リップシンク", "--org02", help="Organization 2 name"),
    org03_name: str = typer.Option("YAML拡張", "--org03", help="Organization 3 name"),
    org04_name: str = typer.Option("エージェント文書検索", "--org04", help="Organization 4 name"),
    org01_workspace: str = typer.Option("video-model-workspace", "--ws01", help="Organization 1 workspace"),
    org02_workspace: str = typer.Option("lipsync-workspace", "--ws02", help="Organization 2 workspace"),
    org03_workspace: str = typer.Option("yaml-enhancement-workspace", "--ws03", help="Organization 3 workspace"),
    org04_workspace: str = typer.Option("agent-docs-search-workspace", "--ws04", help="Organization 4 workspace"),
    attach: bool = typer.Option(True, "--attach/--no-attach", help="Attach to session after creation"),
):
    """Create 4x4 multiagent tmux session with 4 organizations x 4 roles (boss, worker-a, worker-b, worker-c)"""
    
    config = Config("config.yaml")
    tmux = TmuxSession(config)
    
    # Custom organizations configuration
    organizations = [
        {"id": "org-01", "name": org01_name, "workspace": org01_workspace},
        {"id": "org-02", "name": org02_name, "workspace": org02_workspace},
        {"id": "org-03", "name": org03_name, "workspace": org03_workspace},
        {"id": "org-04", "name": org04_name, "workspace": org04_workspace}
    ]
    
    try:
        typer.echo(f"🚀 Creating 4x4 multiagent environment: '{name}'")
        typer.echo(f"📁 Base path: {base_path}")
        typer.echo("🏢 Organizations:")
        for i, org in enumerate(organizations, 1):
            typer.echo(f"   {i}. {org['id'].upper()}: {org['name']} ({org['workspace']})")
        
        session = tmux.create_multiagent_session(name, base_path, organizations)
        
        typer.echo(f"✅ Created multiagent space '{name}' with 16 panes (4x4 layout)")
        typer.echo("📊 Layout:")
        typer.echo("   Row 1: ORG-01 (Boss | Worker-A | Worker-B | Worker-C)")
        typer.echo("   Row 2: ORG-02 (Boss | Worker-A | Worker-B | Worker-C)")
        typer.echo("   Row 3: ORG-03 (Boss | Worker-A | Worker-B | Worker-C)")
        typer.echo("   Row 4: ORG-04 (Boss | Worker-A | Worker-B | Worker-C)")
        
        if attach:
            typer.echo(f"🔗 Attaching to session '{name}'...")
            # Attach to the tmux session (this will replace the current process)
            tmux.attach_session(name)
            
        return session
        
    except Exception as e:
        logger.error(f"Failed to create multiagent space: {e}")
        raise typer.Exit(1)

@space_app.command()
def attach(
    name: str = typer.Argument(..., help="Space name to attach"),
    readonly: bool = typer.Option(False, help="Attach in readonly mode"),
):
    """Attach to an existing tmux space"""
    config = Config("config.yaml")
    tmux = TmuxSession(config)
    try:
        session = tmux.get_session(name)
        if session:
            typer.echo(f"🔗 Attaching to space '{name}'...")
            # Attach to the tmux session (this will replace the current process)
            tmux.attach_session(name)
        else:
            typer.echo(f"❌ Space '{name}' not found")
            typer.echo("💡 Tip: Use 'haconiwa space list' to see available spaces")
    except Exception as e:
        logger.error(f"Failed to attach to space: {e}")
        raise typer.Exit(1)

@space_app.command()
def resize(
    name: str = typer.Argument(..., help="Space name"),
    layout: str = typer.Option("even-horizontal", help="New layout"),
    pane_id: Optional[int] = typer.Option(None, help="Specific pane to resize"),
    size: Optional[int] = typer.Option(None, help="New size (percentage)"),
):
    """Resize panes or change layout of a tmux space"""
    config = Config("config.yaml")
    tmux = TmuxSession(config)
    try:
        if pane_id and size:
            tmux.resize_pane(name, pane_id, height=size)
        typer.echo(f"🔧 Resized space '{name}' with new layout: {layout}")
    except Exception as e:
        logger.error(f"Failed to resize space: {e}")
        raise typer.Exit(1)

@space_app.command()
def kill(
    name: str = typer.Argument(..., help="Space name"),
    force: bool = typer.Option(False, help="Force kill without confirmation"),
):
    """Kill a tmux space and clean up resources"""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to kill space '{name}'?")
        if not confirm:
            raise typer.Exit()

    config = Config("config.yaml")
    tmux = TmuxSession(config)
    try:
        tmux.kill_session(name)
        typer.echo(f"💀 Killed space '{name}'")
    except Exception as e:
        logger.error(f"Failed to kill space: {e}")
        raise typer.Exit(1)

@space_app.command("list")
def list_spaces(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
):
    """List all active tmux spaces"""
    config = Config("config.yaml")
    tmux = TmuxSession(config)
    try:
        sessions = tmux.list_sessions()
        if not sessions:
            typer.echo("📭 No active spaces found")
            typer.echo("💡 Tip: Create a space with 'haconiwa space create <name>' or 'haconiwa space multiagent'")
            return

        typer.echo("📋 Active tmux spaces:")
        for session in sessions:
            if verbose:
                typer.echo(f"📦 Space: {session['name']}")
                typer.echo(f"   🪟 Windows: {session['windows']}")
                typer.echo(f"   📅 Created: {session['created']}")
                typer.echo(f"   🔗 Attached: {'Yes' if session['attached'] else 'No'}")
                typer.echo("   ---")
            else:
                attached_icon = "🔗" if session['attached'] else "📦"
                typer.echo(f"   {attached_icon} {session['name']} ({session['windows']} windows)")
    except Exception as e:
        logger.error(f"Failed to list spaces: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    space_app()