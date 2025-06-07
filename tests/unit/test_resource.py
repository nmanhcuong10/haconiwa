import pytest
from pathlib import Path
from src.haconiwa.resource.path_scanner import PathScanner
from src.haconiwa.resource.db_fetcher import DBFetcher
import sqlite3

def test_file_scan():
    scanner = PathScanner()
    result = scanner.scan_directory("/path/to/test/directory")
    assert isinstance(result, list)
    assert all(isinstance(file, Path) for file in result)

def test_file_formats():
    scanner = PathScanner()
    result = scanner.scan_directory("/path/to/test/directory", extensions=[".txt", ".md"])
    assert all(file.suffix in [".txt", ".md"] for file in result)

def test_large_file_handling():
    scanner = PathScanner()
    result = scanner.scan_directory("/path/to/large/files")
    assert len(result) > 1000

def test_db_connection():
    fetcher = DBFetcher("sqlite:///test.db")
    connection = fetcher.get_connection()
    assert isinstance(connection, sqlite3.Connection)

def test_db_query():
    fetcher = DBFetcher("sqlite:///test.db")
    result = fetcher.execute_query("SELECT * FROM test_table")
    assert isinstance(result, list)

def test_db_error_handling():
    fetcher = DBFetcher("sqlite:///non_existent.db")
    with pytest.raises(sqlite3.OperationalError):
        fetcher.get_connection()