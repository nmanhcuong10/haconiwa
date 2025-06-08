import typer
from typing import Optional, List
from pathlib import Path
import subprocess

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
    org01_name: str = typer.Option("", "--org01-name", help="Organization 1 name (optional)"),
    org02_name: str = typer.Option("", "--org02-name", help="Organization 2 name (optional)"),
    org03_name: str = typer.Option("", "--org03-name", help="Organization 3 name (optional)"),
    org04_name: str = typer.Option("", "--org04-name", help="Organization 4 name (optional)"),
    task01_name: str = typer.Option("", "--task01", help="Task name for organization 1 (optional)"),
    task02_name: str = typer.Option("", "--task02", help="Task name for organization 2 (optional)"),
    task03_name: str = typer.Option("", "--task03", help="Task name for organization 3 (optional)"),
    task04_name: str = typer.Option("", "--task04", help="Task name for organization 4 (optional)"),
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
        {"id": "org-01", "org_name": org01_name, "task_name": task01_name, "workspace": org01_workspace},
        {"id": "org-02", "org_name": org02_name, "task_name": task02_name, "workspace": org02_workspace},
        {"id": "org-03", "org_name": org03_name, "task_name": task03_name, "workspace": org03_workspace},
        {"id": "org-04", "org_name": org04_name, "task_name": task04_name, "workspace": org04_workspace}
    ]
    
    try:
        typer.echo(f"🚀 Creating 4x4 multiagent environment: '{name}'")
        typer.echo(f"📁 Base path: {base_path}")
        typer.echo("🏢 Organizations:")
        for i, org in enumerate(organizations, 1):
            org_display = f"{org['org_name']}" if org['org_name'] else f"{org['id'].upper()}"
            task_display = f" - {org['task_name']}" if org['task_name'] else ""
            typer.echo(f"   {i}. {org_display}{task_display} ({org['workspace']})")
        
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
    try:
        # Check if session exists using tmux directly
        result = subprocess.run(['tmux', 'has-session', '-t', name], 
                              capture_output=True, check=False)
        
        if result.returncode == 0:
            typer.echo(f"🔗 Attaching to space '{name}'...")
            # Attach using direct tmux command
            if readonly:
                subprocess.run(['tmux', 'attach-session', '-t', name, '-r'], check=True)
            else:
                subprocess.run(['tmux', 'attach-session', '-t', name], check=True)
        else:
            typer.echo(f"❌ Space '{name}' not found")
            typer.echo("💡 Tip: Use 'haconiwa space list' to see available spaces")
            
            # Show available sessions
            list_result = subprocess.run(['tmux', 'list-sessions'], 
                                       capture_output=True, text=True, check=False)
            if list_result.returncode == 0 and list_result.stdout.strip():
                typer.echo("\n📋 Available tmux sessions:")
                for line in list_result.stdout.strip().split('\n'):
                    session_name = line.split(':')[0]
                    typer.echo(f"   📦 {session_name}")
            else:
                typer.echo("📭 No tmux sessions found")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to attach to space: {e}")
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ tmux is not installed or not found in PATH")
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
    try:
        # Get tmux sessions directly
        result = subprocess.run(['tmux', 'list-sessions'], 
                              capture_output=True, text=True, check=False)
        
        if result.returncode == 0 and result.stdout.strip():
            typer.echo("📋 Active company spaces:")
            
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 2:
                    session_name = parts[0]
                    session_info = parts[1].strip()
                    
                    # Check if attached
                    attached = "(attached)" in line
                    attached_icon = "🔗" if attached else "📦"
                    
                    if verbose:
                        typer.echo(f"{attached_icon} Space: {session_name}")
                        typer.echo(f"   📅 Info: {session_info}")
                        typer.echo("   ---")
                    else:
                        typer.echo(f"   {attached_icon} {session_name}")
        else:
            typer.echo("📭 No active spaces found")
            typer.echo("💡 Tip: Create a space with 'haconiwa space create <name>' or 'haconiwa space multiagent'")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list spaces: {e}")
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ tmux is not installed or not found in PATH")
        raise typer.Exit(1)

if __name__ == "__main__":
    space_app()