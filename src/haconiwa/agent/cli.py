import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from haconiwa.agent.base import BaseAgent
from haconiwa.agent.boss import BossAgent
from haconiwa.agent.worker import WorkerAgent, WorkerSpecialty
from haconiwa.agent.manager import AgentManager
from haconiwa.core.config import Config

console = Console()
agent_app = typer.Typer(help="エージェント管理コマンド (開発中)")

@agent_app.command()
def spawn(
    agent_type: str = typer.Argument(..., help="Agent type (boss/worker/manager)"),
    agent_id: str = typer.Option("auto", help="Agent ID"),
    config_file: Optional[str] = typer.Option(None, help="Configuration file path"),
):
    """Spawn a new agent"""
    try:
        config = Config(config_file or "config.yaml")
        
        if agent_type == "boss":
            agent = BossAgent(agent_id, config)
        elif agent_type == "worker":
            agent = WorkerAgent(agent_id, WorkerSpecialty.FRONTEND, config)
        elif agent_type == "manager":
            agent = AgentManager()
        else:
            rprint(f"[red]Error:[/red] Unknown agent type: {agent_type}")
            raise typer.Exit(1)
            
        rprint(f"[green]✓[/green] Agent '{agent_id}' ({agent_type}) spawned successfully")
        
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@agent_app.command()
def ps():
    """List running agents"""
    try:
        table = Table(title="Running Agents")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Uptime", style="white")

        # Placeholder data - in real implementation would query actual agents
        table.add_row("boss-1", "Boss", "Running", "2h 30m")
        table.add_row("worker-1", "Worker", "Idle", "1h 45m")
        table.add_row("manager-1", "Manager", "Active", "3h 10m")

        console.print(table)
        
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@agent_app.command()
def stop(
    agent_id: str = typer.Argument(..., help="Agent ID to stop"),
    force: bool = typer.Option(False, help="Force stop without confirmation"),
):
    """Stop a running agent"""
    if not force:
        confirm = typer.confirm(f"Stop agent '{agent_id}'?")
        if not confirm:
            raise typer.Abort()

    try:
        rprint(f"[yellow]Stopping agent '{agent_id}'...[/yellow]")
        # Implementation would stop the actual agent
        rprint(f"[green]✓[/green] Agent '{agent_id}' stopped successfully")
        
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@agent_app.command()
def logs(
    agent_id: str = typer.Argument(..., help="Agent ID"),
    follow: bool = typer.Option(False, help="Follow log output"),
    lines: int = typer.Option(50, help="Number of lines to show"),
):
    """Show agent logs"""
    try:
        rprint(f"[blue]Showing logs for agent '{agent_id}' (last {lines} lines)[/blue]")
        
        # Placeholder logs - in real implementation would read actual logs
        sample_logs = [
            "2024-01-01 10:00:00 - INFO - Agent started",
            "2024-01-01 10:00:01 - INFO - Initialized successfully", 
            "2024-01-01 10:00:02 - INFO - Waiting for tasks",
            "2024-01-01 10:05:00 - INFO - Received task: example_task",
            "2024-01-01 10:05:01 - INFO - Task completed successfully",
        ]
        
        for log in sample_logs[-lines:]:
            console.print(log)
            
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@agent_app.command()
def shell(
    agent_id: str = typer.Argument(..., help="Agent ID"),
):
    """Connect to agent shell for debugging"""
    try:
        rprint(f"[blue]Connecting to agent '{agent_id}' shell...[/blue]")
        rprint(f"[yellow]Note:[/yellow] Shell connection not implemented in demo")
        
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    agent_app()