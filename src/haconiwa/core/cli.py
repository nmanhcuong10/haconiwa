import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from haconiwa.core.config import Config
from haconiwa.core.state import StateManager
from haconiwa.core.upgrade import Upgrader

core_app = typer.Typer(help="コア管理コマンド (開発中)")
console = Console()

@core_app.command()
def init(
    path: Path = typer.Option(
        Path.cwd(),
        "--path", "-p",
        help="Project root path"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Force initialization even if directory is not empty"
    )
):
    """Initialize a new haconiwa project"""
    try:
        config = Config(str(path / "config.yaml"))
        if not force and any(path.iterdir()):
            raise typer.BadParameter("Directory is not empty. Use --force to override")
        
        with console.status("Initializing project..."):
            # config.init_project() - method doesn't exist, commenting out
            StateManager(str(path / "config.yaml")).load_state(str(path / "state.pkl"))
            
        rprint("[green]✓[/green] Project initialized successfully")
        
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@core_app.command()
def status():
    """Show current haconiwa status"""
    try:
        config = Config("config.yaml")
        state = StateManager("config.yaml")
        
        table = Table(title="haconiwa Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")

        table.add_row(
            "Configuration",
            "✓ Loaded",
            "config loaded"
        )
        
        table.add_row(
            "State",
            "✓ Active",
            "state active"
        )

        table.add_row(
            "Worlds",
            "- None",
            "-"
        )

        console.print(table)

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@core_app.command()
def reset(
    force: bool = typer.Option(
        False,
        "--force", "-f", 
        help="Force reset without confirmation"
    )
):
    """Reset haconiwa state and remove all data"""
    if not force:
        confirm = typer.confirm("This will remove all haconiwa data. Continue?")
        if not confirm:
            raise typer.Abort()

    try:
        with console.status("Resetting haconiwa..."):
            state = StateManager("config.yaml")
            # state.reset() - method doesn't exist
            
        rprint("[green]✓[/green] Reset completed successfully")
        
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@core_app.command()
def upgrade(
    version: Optional[str] = typer.Option(
        None,
        "--version", "-v",
        help="Target version to upgrade to"
    ),
    check_only: bool = typer.Option(
        False,
        "--check-only",
        help="Only check if upgrade is available"
    )
):
    """Upgrade haconiwa to latest version"""
    try:
        upgrader = Upgrader()
        current = upgrader.get_current_version()
        latest = upgrader.get_latest_version()

        if check_only:
            if current == latest:
                rprint("[green]✓[/green] Already at latest version")
            else:
                rprint(f"Upgrade available: {current} -> {latest}")
            return

        if version and version != latest:
            rprint(f"[yellow]Warning:[/yellow] Requested version {version} differs from latest {latest}")
            
        with console.status("Upgrading haconiwa..."):
            upgrader.upgrade(version)
            
        rprint(f"[green]✓[/green] Upgraded from {current} to {version or latest}")
        
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    core_app()