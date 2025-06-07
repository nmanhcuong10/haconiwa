import typer
from haconiwa.resource.path_scanner import PathScanner
from haconiwa.resource.db_fetcher import DBFetcher

resource_app = typer.Typer(help="リソース管理 (開発中)")

@resource_app.command()
def scan(directory: str, extension: str = ""):
    """ファイルパススキャンと拡張子フィルタ"""
    scanner = PathScanner(directory, extension)
    results = scanner.scan()
    typer.echo(f"スキャン結果: {results}")

@resource_app.command()
def pull(query: str):
    """データベースクエリ実行とデータ取得"""
    fetcher = DBFetcher()
    results = fetcher.execute_query(query)
    typer.echo(f"クエリ結果: {results}")

@resource_app.command()
def sync(remote: str):
    """リモートストレージ同期（S3/GCS等）"""
    typer.echo(f"{remote} との同期を開始します...")
    # リモートストレージ同期処理を実装
    typer.echo("同期が完了しました。")

if __name__ == "__main__":
    resource_app()