import functools
import typing
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

import click
import rich.console
import rich.progress
import rich.table
import typer
from rich.style import Style
from typer import Option, Typer
from typer.models import CommandInfo, Context, ParamInfo

T = TypeVar("T")
console = rich.console.Console()

def common_options(f: Callable) -> Callable:
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    
    options = [
        Option(["--verbose"], is_flag=True, help="詳細なログ出力を有効化"),
        Option(["--quiet"], is_flag=True, help="ログ出力を最小限に抑制"),
        Option(["--config"], help="設定ファイルのパス"),
        Option(["--no-color"], is_flag=True, help="カラー出力を無効化"),
    ]
    
    for option in reversed(options):
        wrapper = option(wrapper)
    return wrapper

def validate_input(type_: Type[T], min_value: Optional[T] = None, max_value: Optional[T] = None):
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            for arg in args:
                if isinstance(arg, type_):
                    if min_value is not None and arg < min_value:
                        raise typer.BadParameter(f"値は {min_value} 以上である必要があります")
                    if max_value is not None and arg > max_value:
                        raise typer.BadParameter(f"値は {max_value} 以下である必要があります")
            return f(*args, **kwargs)
        return wrapper
    return decorator

def progress_bar(desc: str = "処理中..."):
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            with rich.progress.Progress() as progress:
                task = progress.add_task(desc, total=100)
                result = f(*args, progress=progress, task_id=task, **kwargs)
                progress.update(task, completed=100)
                return result
        return wrapper
    return decorator

def format_output(data: Union[List, Dict], table: bool = False):
    if table and isinstance(data, List):
        table = rich.table.Table()
        if data:
            for key in data[0].keys():
                table.add_column(str(key))
            for row in data:
                table.add_row(*[str(v) for v in row.values()])
        console.print(table)
    else:
        console.print(data)

def error_handler(f: Callable) -> Callable:
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            console.print(f"[red]エラー: {str(e)}[/red]")
            raise typer.Exit(1)
    return wrapper

def command_group(name: str) -> Typer:
    app = Typer(name=name)
    
    @app.callback()
    def callback():
        """haconiwa コマンドグループ"""
        pass
    
    return app

def confirm_action(message: str = "続行しますか?"):
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if typer.confirm(message):
                return f(*args, **kwargs)
            raise typer.Abort()
        return wrapper
    return decorator

def style_text(text: str, style: str) -> str:
    return f"[{style}]{text}[/{style}]"

def success(message: str):
    console.print(f"[green]✓ {message}[/green]")

def warning(message: str):
    console.print(f"[yellow]! {message}[/yellow]")

def error(message: str):
    console.print(f"[red]✗ {message}[/red]")

def debug(message: str):
    if typer.get_current_context().obj.get("verbose"):
        console.print(f"[dim]{message}[/dim]")