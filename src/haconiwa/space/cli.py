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
            typer.echo(f"Attached to space '{name}'")
        else:
            typer.echo(f"Space '{name}' not found")
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
        typer.echo(f"Resized space '{name}' with new layout: {layout}")
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
        typer.echo(f"Killed space '{name}'")
    except Exception as e:
        logger.error(f"Failed to kill space: {e}")
        raise typer.Exit(1)

@space_app.command()
def list_spaces(
    verbose: bool = typer.Option(False, help="Show detailed information"),
):
    """List all active tmux spaces"""
    config = Config("config.yaml")
    tmux = TmuxSession(config)
    try:
        sessions = tmux.list_sessions()
        if not sessions:
            typer.echo("No active spaces found")
            return

        for session in sessions:
            if verbose:
                typer.echo(f"Space: {session['name']}")
                typer.echo(f"  Windows: {session['windows']}")
                typer.echo(f"  Created: {session['created']}")
                typer.echo(f"  Attached: {session['attached']}")
                typer.echo("---")
            else:
                typer.echo(session['name'])
    except Exception as e:
        logger.error(f"Failed to list spaces: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    space_app()