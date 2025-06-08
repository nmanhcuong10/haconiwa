#!/usr/bin/env python3
"""
Pre-release check script for haconiwa project.
Performs comprehensive checks before release: tests, linting, security, etc.
"""

import sys
import subprocess
import os
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import json
import time

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
            timeout=600  # 10 minutes timeout for full test suite
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out after 10 minutes"
    except Exception as e:
        return 1, "", str(e)

def check_git_status(project_root: Path) -> Dict[str, Any]:
    """Check git repository status"""
    console.print("🔍 [bold blue]Checking git status...[/bold blue]")
    
    # Check if we're in a git repository
    cmd = ["git", "status", "--porcelain"]
    returncode, stdout, stderr = run_command(cmd, project_root)
    
    if returncode != 0:
        return {"success": False, "error": "Not a git repository or git not available"}
    
    # Check for uncommitted changes
    uncommitted_files = [line.strip() for line in stdout.split('\n') if line.strip()]
    
    # Check current branch
    cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    returncode, branch_stdout, _ = run_command(cmd, project_root)
    current_branch = branch_stdout.strip() if returncode == 0 else "unknown"
    
    # Check if we're ahead/behind remote
    cmd = ["git", "status", "--porcelain=v1", "--branch"]
    returncode, status_stdout, _ = run_command(cmd, project_root)
    
    is_clean = len(uncommitted_files) == 0
    
    result = {
        "success": True,
        "is_clean": is_clean,
        "uncommitted_files": uncommitted_files,
        "current_branch": current_branch,
        "status_output": status_stdout
    }
    
    if is_clean:
        console.print("✅ [green]Git status is clean[/green]")
    else:
        console.print(f"⚠️ [yellow]Found {len(uncommitted_files)} uncommitted changes[/yellow]")
        for file in uncommitted_files[:5]:  # Show first 5 files
            console.print(f"  • {file}")
        if len(uncommitted_files) > 5:
            console.print(f"  ... and {len(uncommitted_files) - 5} more files")
    
    return result

def run_full_test_suite(project_root: Path) -> Dict[str, Any]:
    """Run complete test suite"""
    console.print("🧪 [bold blue]Running full test suite...[/bold blue]")
    
    # Run unit tests
    console.print("  • Running unit tests...")
    cmd = ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"]
    unit_returncode, unit_stdout, unit_stderr = run_command(cmd, project_root)
    
    # Run integration tests  
    console.print("  • Running integration tests...")
    cmd = ["python", "-m", "pytest", "tests/integration/", "-v", "--tb=short"]
    integration_returncode, integration_stdout, integration_stderr = run_command(cmd, project_root)
    
    # Run with coverage
    console.print("  • Running coverage analysis...")
    cmd = ["python", "-m", "pytest", "--cov=haconiwa", "--cov-report=term", "--cov-fail-under=70"]
    coverage_returncode, coverage_stdout, coverage_stderr = run_command(cmd, project_root)
    
    all_passed = unit_returncode == 0 and integration_returncode == 0 and coverage_returncode == 0
    
    result = {
        "success": all_passed,
        "unit_tests": {"returncode": unit_returncode, "stdout": unit_stdout, "stderr": unit_stderr},
        "integration_tests": {"returncode": integration_returncode, "stdout": integration_stdout, "stderr": integration_stderr},
        "coverage": {"returncode": coverage_returncode, "stdout": coverage_stdout, "stderr": coverage_stderr}
    }
    
    if all_passed:
        console.print("✅ [green]All tests passed[/green]")
    else:
        console.print("❌ [red]Some tests failed[/red]")
        if unit_returncode != 0:
            console.print("  • Unit tests failed")
        if integration_returncode != 0:
            console.print("  • Integration tests failed")
        if coverage_returncode != 0:
            console.print("  • Coverage check failed")
    
    return result

def check_code_quality(project_root: Path) -> Dict[str, Any]:
    """Run code quality checks"""
    console.print("🔍 [bold blue]Running code quality checks...[/bold blue]")
    
    results = {}
    
    # Black formatting check
    console.print("  • Checking code formatting (black)...")
    cmd = ["python", "-m", "black", "--check", "src/", "tests/"]
    black_returncode, black_stdout, black_stderr = run_command(cmd, project_root)
    results["black"] = {"returncode": black_returncode, "stdout": black_stdout, "stderr": black_stderr}
    
    # flake8 linting
    console.print("  • Running linter (flake8)...")
    cmd = ["python", "-m", "flake8", "src/", "tests/"]
    flake8_returncode, flake8_stdout, flake8_stderr = run_command(cmd, project_root)
    results["flake8"] = {"returncode": flake8_returncode, "stdout": flake8_stdout, "stderr": flake8_stderr}
    
    # mypy type checking
    console.print("  • Running type checker (mypy)...")
    cmd = ["python", "-m", "mypy", "src/haconiwa"]
    mypy_returncode, mypy_stdout, mypy_stderr = run_command(cmd, project_root)
    results["mypy"] = {"returncode": mypy_returncode, "stdout": mypy_stdout, "stderr": mypy_stderr}
    
    all_passed = all(result["returncode"] == 0 for result in results.values())
    
    if all_passed:
        console.print("✅ [green]Code quality checks passed[/green]")
    else:
        console.print("⚠️ [yellow]Some code quality issues found[/yellow]")
        for tool, result in results.items():
            if result["returncode"] != 0:
                console.print(f"  • {tool} found issues")
    
    return {"success": all_passed, "results": results}

def check_security(project_root: Path) -> Dict[str, Any]:
    """Run security checks"""
    console.print("🔒 [bold blue]Running security checks...[/bold blue]")
    
    # Bandit security linter
    console.print("  • Running security linter (bandit)...")
    cmd = ["python", "-m", "bandit", "-r", "src/", "-f", "json"]
    bandit_returncode, bandit_stdout, bandit_stderr = run_command(cmd, project_root)
    
    result = {"returncode": bandit_returncode, "stdout": bandit_stdout, "stderr": bandit_stderr}
    
    if bandit_returncode == 0:
        console.print("✅ [green]Security checks passed[/green]")
    else:
        console.print("⚠️ [yellow]Security issues found[/yellow]")
        try:
            bandit_results = json.loads(bandit_stdout)
            if "results" in bandit_results:
                console.print(f"  • Found {len(bandit_results['results'])} security issues")
        except:
            pass
    
    return {"success": bandit_returncode == 0, "result": result}

def check_package_build(project_root: Path) -> Dict[str, Any]:
    """Check if package can be built"""
    console.print("📦 [bold blue]Checking package build...[/bold blue]")
    
    # Clean previous builds
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)
    
    # Build package
    cmd = ["python", "-m", "build"]
    returncode, stdout, stderr = run_command(cmd, project_root)
    
    result = {"returncode": returncode, "stdout": stdout, "stderr": stderr}
    
    if returncode == 0:
        console.print("✅ [green]Package build successful[/green]")
        
        # Check if wheel and source dist were created
        if dist_dir.exists():
            files = list(dist_dir.glob("*"))
            console.print(f"  • Created {len(files)} distribution files")
    else:
        console.print("❌ [red]Package build failed[/red]")
    
    return {"success": returncode == 0, "result": result}

def generate_prerelease_report(results: Dict[str, Any]) -> None:
    """Generate and display prerelease report"""
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        "[bold blue]📋 Pre-Release Check Report[/bold blue]",
        border_style="blue"
    ))
    
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Details")
    
    for check_name, result in results.items():
        if result.get("success", False):
            status = "✅ PASS"
            details = "OK"
        else:
            status = "❌ FAIL"
            if "error" in result:
                details = result["error"]
            else:
                details = "Issues found"
        
        table.add_row(check_name.replace("_", " ").title(), status, details)
    
    console.print(table)
    
    # Overall status
    all_passed = all(result.get("success", False) for result in results.values())
    
    if all_passed:
        console.print("\n🎉 [bold green]All pre-release checks passed! Ready for release.[/bold green]")
    else:
        console.print("\n⚠️ [bold red]Some checks failed. Please fix issues before release.[/bold red]")
        console.print("\n💡 [yellow]Tips for fixing common issues:[/yellow]")
        console.print("• Run 'black src/ tests/' to fix formatting")
        console.print("• Run 'haconiwa-test all' to see detailed test failures")
        console.print("• Check security issues with 'bandit -r src/'")

def main(
    skip_tests: bool = typer.Option(False, "--skip-tests", help="Skip running tests"),
    skip_quality: bool = typer.Option(False, "--skip-quality", help="Skip code quality checks"),
    skip_security: bool = typer.Option(False, "--skip-security", help="Skip security checks"),
    skip_build: bool = typer.Option(False, "--skip-build", help="Skip package build check"),
    fix_formatting: bool = typer.Option(False, "--fix", help="Automatically fix formatting issues")
):
    """
    Run comprehensive pre-release checks for haconiwa.
    
    This script performs the following checks:
    • Git repository status
    • Full test suite (unit + integration + coverage)
    • Code quality (formatting, linting, type checking)
    • Security analysis
    • Package build verification
    """
    try:
        project_root = find_project_root()
    except FileNotFoundError as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold blue]🚀 Haconiwa Pre-Release Checks[/bold blue]\n"
        f"Project root: {project_root}",
        border_style="blue"
    ))
    
    # Auto-fix formatting if requested
    if fix_formatting:
        console.print("🔧 [bold blue]Auto-fixing formatting...[/bold blue]")
        cmd = ["python", "-m", "black", "src/", "tests/"]
        returncode, stdout, stderr = run_command(cmd, project_root)
        if returncode == 0:
            console.print("✅ [green]Formatting fixed[/green]")
        else:
            console.print("❌ [red]Failed to fix formatting[/red]")
    
    results = {}
    
    # Run checks
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        
        # Git status check
        task = progress.add_task("Checking git status...", total=100)
        results["git_status"] = check_git_status(project_root)
        progress.update(task, completed=100)
        
        # Test suite
        if not skip_tests:
            task = progress.add_task("Running test suite...", total=100)
            results["test_suite"] = run_full_test_suite(project_root)
            progress.update(task, completed=100)
        
        # Code quality
        if not skip_quality:
            task = progress.add_task("Checking code quality...", total=100)
            results["code_quality"] = check_code_quality(project_root)
            progress.update(task, completed=100)
        
        # Security
        if not skip_security:
            task = progress.add_task("Running security checks...", total=100)
            results["security"] = check_security(project_root)
            progress.update(task, completed=100)
        
        # Package build
        if not skip_build:
            task = progress.add_task("Checking package build...", total=100)
            results["package_build"] = check_package_build(project_root)
            progress.update(task, completed=100)
    
    # Generate report
    generate_prerelease_report(results)
    
    # Exit with appropriate code
    all_passed = all(result.get("success", False) for result in results.values())
    sys.exit(0 if all_passed else 1)

def run_prerelease_checks():
    """Entry point for haconiwa-prerelease command"""
    typer.run(main)

if __name__ == "__main__":
    run_prerelease_checks() 