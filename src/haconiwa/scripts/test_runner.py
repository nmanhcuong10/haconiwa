#!/usr/bin/env python3
"""
Test runner script for haconiwa project.
Provides unified test execution interface for development and CI.
"""

import sys
import subprocess
import os
import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def find_project_root() -> Path:
    """Find the project root directory by looking for pyproject.toml"""
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root (no pyproject.toml found)")

def run_command(cmd: List[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """Run a command and return return code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out after 5 minutes"
    except Exception as e:
        return 1, "", str(e)

def run_unit_tests(project_root: Path) -> bool:
    """Run unit tests"""
    console.print("\n🧪 [bold blue]Running unit tests...[/bold blue]")
    
    cmd = ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"]
    returncode, stdout, stderr = run_command(cmd, project_root)
    
    if returncode == 0:
        console.print("✅ [green]Unit tests passed[/green]")
        return True
    else:
        console.print("❌ [red]Unit tests failed[/red]")
        console.print(f"[red]Error output:[/red]\n{stderr}")
        if stdout:
            console.print(f"[yellow]Test output:[/yellow]\n{stdout}")
        return False

def run_integration_tests(project_root: Path) -> bool:
    """Run integration tests"""
    console.print("\n🔗 [bold blue]Running integration tests...[/bold blue]")
    
    cmd = ["python", "-m", "pytest", "tests/integration/", "-v", "--tb=short"]
    returncode, stdout, stderr = run_command(cmd, project_root)
    
    if returncode == 0:
        console.print("✅ [green]Integration tests passed[/green]")
        return True
    else:
        console.print("❌ [red]Integration tests failed[/red]")
        console.print(f"[red]Error output:[/red]\n{stderr}")
        if stdout:
            console.print(f"[yellow]Test output:[/yellow]\n{stdout}")
        return False

def run_specific_test(project_root: Path, test_path: str) -> bool:
    """Run specific test file or directory"""
    console.print(f"\n🎯 [bold blue]Running specific test: {test_path}[/bold blue]")
    
    cmd = ["python", "-m", "pytest", test_path, "-v", "--tb=short"]
    returncode, stdout, stderr = run_command(cmd, project_root)
    
    if returncode == 0:
        console.print(f"✅ [green]Test {test_path} passed[/green]")
        return True
    else:
        console.print(f"❌ [red]Test {test_path} failed[/red]")
        console.print(f"[red]Error output:[/red]\n{stderr}")
        if stdout:
            console.print(f"[yellow]Test output:[/yellow]\n{stdout}")
        return False

def run_test_coverage(project_root: Path) -> bool:
    """Run tests with coverage reporting"""
    console.print("\n📊 [bold blue]Running tests with coverage...[/bold blue]")
    
    cmd = ["python", "-m", "pytest", "--cov=haconiwa", "--cov-report=term", "--cov-report=html"]
    returncode, stdout, stderr = run_command(cmd, project_root)
    
    if returncode == 0:
        console.print("✅ [green]Coverage tests completed[/green]")
        console.print("📄 [blue]HTML coverage report generated in htmlcov/[/blue]")
        return True
    else:
        console.print("❌ [red]Coverage tests failed[/red]")
        console.print(f"[red]Error output:[/red]\n{stderr}")
        return False

def check_test_environment(project_root: Path) -> bool:
    """Check if test environment is properly set up"""
    console.print("🔍 [bold blue]Checking test environment...[/bold blue]")
    
    # Check if pytest is available
    cmd = ["python", "-m", "pytest", "--version"]
    returncode, stdout, stderr = run_command(cmd, project_root)
    
    if returncode != 0:
        console.print("❌ [red]pytest is not available[/red]")
        console.print("💡 [yellow]Install test dependencies: pip install -e .[dev][/yellow]")
        return False
    
    # Check if tests directory exists
    if not (project_root / "tests").exists():
        console.print("❌ [red]tests directory not found[/red]")
        return False
    
    console.print("✅ [green]Test environment is ready[/green]")
    return True

def main(
    test_type: str = typer.Argument("all", help="Type of tests to run: all, unit, integration, coverage"),
    test_path: Optional[str] = typer.Option(None, "--test", "-t", help="Specific test file or directory to run"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    fast: bool = typer.Option(False, "--fast", "-f", help="Skip slower integration tests")
):
    """
    Run haconiwa tests with various options.
    
    Examples:
        haconiwa-test all          # Run all tests
        haconiwa-test unit         # Run only unit tests  
        haconiwa-test integration  # Run only integration tests
        haconiwa-test coverage     # Run tests with coverage
        haconiwa-test --test tests/unit/test_core.py  # Run specific test
    """
    try:
        project_root = find_project_root()
    except FileNotFoundError as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold blue]🧪 Haconiwa Test Runner[/bold blue]\n"
        f"Project root: {project_root}\n"
        f"Test type: {test_type}",
        border_style="blue"
    ))
    
    # Check environment first
    if not check_test_environment(project_root):
        sys.exit(1)
    
    success = True
    
    if test_path:
        # Run specific test
        success = run_specific_test(project_root, test_path)
    elif test_type == "unit":
        success = run_unit_tests(project_root)
    elif test_type == "integration":
        if fast:
            console.print("⚡ [yellow]Skipping integration tests (fast mode)[/yellow]")
        else:
            success = run_integration_tests(project_root)
    elif test_type == "coverage":
        success = run_test_coverage(project_root)
    elif test_type == "all":
        success = True
        
        # Run unit tests first
        if not run_unit_tests(project_root):
            success = False
        
        # Run integration tests if not in fast mode
        if not fast:
            if not run_integration_tests(project_root):
                success = False
        else:
            console.print("⚡ [yellow]Skipping integration tests (fast mode)[/yellow]")
    else:
        console.print(f"❌ [red]Unknown test type: {test_type}[/red]")
        console.print("Valid types: all, unit, integration, coverage")
        sys.exit(1)
    
    if success:
        console.print("\n🎉 [bold green]All tests completed successfully![/bold green]")
        sys.exit(0)
    else:
        console.print("\n💥 [bold red]Some tests failed![/bold red]")
        sys.exit(1)

def run_tests():
    """Entry point for haconiwa-test command"""
    typer.run(main)

if __name__ == "__main__":
    run_tests() 