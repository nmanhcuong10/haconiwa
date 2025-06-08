import typer
from typing import Optional
from pathlib import Path
import logging
import sys

from haconiwa.core.cli import core_app
from haconiwa.world.cli import world_app
from haconiwa.space.cli import company_app
from haconiwa.resource.cli import resource_app
from haconiwa.agent.cli import agent_app
from haconiwa.task.cli import task_app
from haconiwa.watch.cli import watch_app

app = typer.Typer(
    name="haconiwa",
    help="AI協調開発支援Python CLIツール (開発中)",
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
        typer.echo(f"haconiwa version: {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="詳細なログ出力を有効化"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="設定ファイルのパス"),
    version: bool = typer.Option(False, "--version", callback=version_callback, help="バージョン情報を表示"),
):
    """箱庭 (haconiwa) - AI協調開発支援ツール (開発中)"""
    setup_logging(verbose)
    if config:
        try:
            from haconiwa.core.config import load_config
            load_config(config)
        except Exception as e:
            typer.echo(f"設定ファイルの読み込みに失敗: {e}", err=True)
            sys.exit(1)

app.add_typer(core_app, name="core")
app.add_typer(world_app, name="world")
app.add_typer(company_app, name="company")
app.add_typer(resource_app, name="resource")
app.add_typer(agent_app, name="agent")
app.add_typer(task_app, name="task")
app.add_typer(watch_app, name="watch")

if __name__ == "__main__":
    app()