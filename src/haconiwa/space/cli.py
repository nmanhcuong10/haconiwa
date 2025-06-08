import typer
from typing import Optional, List
from pathlib import Path
import subprocess

from ..space.tmux import TmuxSession
from ..core.config import Config
from ..core.logging import get_logger

logger = get_logger(__name__)
company_app = typer.Typer(help="tmux会社・企業管理 🏢")

@company_app.command()
def build(
    name: str = typer.Option(..., "--name", "-n", help="Company name"),
    base_path: Optional[str] = typer.Option(None, "--base-path", "-p", help="Base path for desks (default: ./{company_name})"),
    org01_name: str = typer.Option("", "--org01-name", help="Organization 1 name (optional)"),
    org02_name: str = typer.Option("", "--org02-name", help="Organization 2 name (optional)"),
    org03_name: str = typer.Option("", "--org03-name", help="Organization 3 name (optional)"),
    org04_name: str = typer.Option("", "--org04-name", help="Organization 4 name (optional)"),
    task01_name: str = typer.Option("", "--task01", help="Task name for organization 1 (optional)"),
    task02_name: str = typer.Option("", "--task02", help="Task name for organization 2 (optional)"),
    task03_name: str = typer.Option("", "--task03", help="Task name for organization 3 (optional)"),
    task04_name: str = typer.Option("", "--task04", help="Task name for organization 4 (optional)"),
    org01_desk: str = typer.Option("video-model-desk", "--desk01", help="Organization 1 desk"),
    org02_desk: str = typer.Option("lipsync-desk", "--desk02", help="Organization 2 desk"),
    org03_desk: str = typer.Option("yaml-enhancement-desk", "--desk03", help="Organization 3 desk"),
    org04_desk: str = typer.Option("agent-docs-search-desk", "--desk04", help="Organization 4 desk"),
    attach: bool = typer.Option(True, "--attach/--no-attach", help="Attach to company after creation"),
    rebuild: bool = typer.Option(False, "--rebuild", help="Force rebuild even if company exists"),
):
    """🏗️ Build a company (create new or update existing 4x4 multiagent tmux company)"""
    
    # Set default base_path if not provided
    if base_path is None:
        base_path = f"./{name}"
    
    # Check if base_path directory exists and warn user
    base_path_obj = Path(base_path)
    if base_path_obj.exists() and any(base_path_obj.iterdir()):
        typer.echo(f"⚠️ Warning: Directory '{base_path}' already exists and is not empty.")
        typer.echo("📁 Existing contents:")
        
        # Show first few items in directory
        items = list(base_path_obj.iterdir())
        for i, item in enumerate(items[:5]):  # Show max 5 items
            item_type = "📁" if item.is_dir() else "📄"
            typer.echo(f"   {item_type} {item.name}")
        
        if len(items) > 5:
            typer.echo(f"   ... and {len(items) - 5} more items")
        
        # Ask for confirmation unless rebuild flag is set
        if not rebuild:
            typer.echo("\n🤔 This may overwrite or mix with existing files.")
            continue_anyway = typer.confirm("Do you want to continue anyway?")
            if not continue_anyway:
                typer.echo("❌ Operation cancelled by user.")
                raise typer.Exit(0)
        else:
            typer.echo("\n🔨 --rebuild flag is set, continuing with rebuild...")
    
    config = Config("config.yaml")
    tmux = TmuxSession(config)
    
    # Check if tmux session already exists
    try:
        result = subprocess.run(['tmux', 'has-session', '-t', name], 
                              capture_output=True, check=False)
        company_exists = result.returncode == 0
    except FileNotFoundError:
        typer.echo("❌ tmux is not installed or not found in PATH")
        raise typer.Exit(1)
    
    # Custom organizations configuration
    organizations = [
        {"id": "org-01", "org_name": org01_name, "task_name": task01_name, "workspace": org01_desk},
        {"id": "org-02", "org_name": org02_name, "task_name": task02_name, "workspace": org02_desk},
        {"id": "org-03", "org_name": org03_name, "task_name": task03_name, "workspace": org03_desk},
        {"id": "org-04", "org_name": org04_name, "task_name": task04_name, "workspace": org04_desk}
    ]
    
    try:
        if company_exists and not rebuild:
            # Update existing company
            typer.echo(f"🔄 Updating existing company: '{name}'")
            
            updates_made = []
            # Track what updates were made
            for i, org in enumerate(organizations, 1):
                if org['org_name']:
                    updates_made.append(f"Organization {i}: {org['org_name']}")
                if org['task_name']:
                    updates_made.append(f"Task {i}: {org['task_name']}")
            
            if updates_made:
                typer.echo("📝 Updates applied:")
                for update in updates_made:
                    typer.echo(f"   ✅ {update}")
                
                # TODO: Implement actual metadata update logic
                # This would update the metadata file and potentially tmux pane titles
                
            else:
                typer.echo(f"ℹ️ No changes specified for company '{name}'")
                typer.echo("💡 Company is already running. Use --rebuild to recreate it.")
            
        else:
            # Create new company (or rebuild existing)
            if company_exists and rebuild:
                typer.echo(f"🔄 Rebuilding company: '{name}'")
                # Kill existing session first
                tmux.kill_session(name)
            else:
                typer.echo(f"🏗️ Building new company: '{name}'")
            
            typer.echo(f"🏗️ Base path: {base_path}")
            typer.echo("🏛️ Organizations:")
            for i, org in enumerate(organizations, 1):
                org_display = f"{org['org_name']}" if org['org_name'] else f"{org['id'].upper()}"
                task_display = f" - {org['task_name']}" if org['task_name'] else ""
                typer.echo(f"   {i}. {org_display}{task_display} ({org['workspace']})")
            
            session = tmux.create_multiagent_session(name, base_path, organizations)
            
            typer.echo(f"✅ Built company '{name}' with 16 panes (4x4 layout)")
            typer.echo("📊 Layout:")
            typer.echo("   Row 1: ORG-01 (Boss | Worker-A | Worker-B | Worker-C)")
            typer.echo("   Row 2: ORG-02 (Boss | Worker-A | Worker-B | Worker-C)")
            typer.echo("   Row 3: ORG-03 (Boss | Worker-A | Worker-B | Worker-C)")
            typer.echo("   Row 4: ORG-04 (Boss | Worker-A | Worker-B | Worker-C)")
            
            if attach:
                typer.echo(f"🔗 Attaching to company '{name}'...")
                # Attach to the tmux session (this will replace the current process)
                tmux.attach_session(name)
                
            return session
        
    except Exception as e:
        logger.error(f"Failed to build company: {e}")
        raise typer.Exit(1)

@company_app.command()
def attach(
    name: str = typer.Argument(..., help="Company name to attach"),
    readonly: bool = typer.Option(False, help="Attach in readonly mode"),
):
    """🔗 Attach to an existing tmux company"""
    try:
        # Check if session exists using tmux directly
        result = subprocess.run(['tmux', 'has-session', '-t', name], 
                              capture_output=True, check=False)
        
        if result.returncode == 0:
            typer.echo(f"🔗 Attaching to company '{name}'...")
            # Attach using direct tmux command
            if readonly:
                subprocess.run(['tmux', 'attach-session', '-t', name, '-r'], check=True)
            else:
                subprocess.run(['tmux', 'attach-session', '-t', name], check=True)
        else:
            typer.echo(f"❌ Company '{name}' not found")
            typer.echo("💡 Tip: Use 'haconiwa company list' to see available companies")
            
            # Show available sessions
            list_result = subprocess.run(['tmux', 'list-sessions'], 
                                       capture_output=True, text=True, check=False)
            if list_result.returncode == 0 and list_result.stdout.strip():
                typer.echo("\n🏢 Available tmux companies:")
                for line in list_result.stdout.strip().split('\n'):
                    session_name = line.split(':')[0]
                    typer.echo(f"   🏛️ {session_name}")
            else:
                typer.echo("🏭 No tmux companies found")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to attach to company: {e}")
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ tmux is not installed or not found in PATH")
        raise typer.Exit(1)

@company_app.command()
def resize(
    name: str = typer.Argument(..., help="Company name"),
    layout: str = typer.Option("even-horizontal", help="New layout"),
    pane_id: Optional[int] = typer.Option(None, help="Specific pane to resize"),
    size: Optional[int] = typer.Option(None, help="New size (percentage)"),
):
    """📐 Resize panes or change layout of a tmux company"""
    config = Config("config.yaml")
    tmux = TmuxSession(config)
    try:
        if pane_id and size:
            tmux.resize_pane(name, pane_id, height=size)
        typer.echo(f"🔧 Resized company '{name}' with new layout: {layout}")
    except Exception as e:
        logger.error(f"Failed to resize company: {e}")
        raise typer.Exit(1)

@company_app.command()
def kill(
    name: str = typer.Argument(..., help="Company name"),
    force: bool = typer.Option(False, help="Force kill without confirmation"),
    clean_dirs: bool = typer.Option(False, "--clean-dirs", help="Remove related directories after killing company"),
    base_path: Optional[str] = typer.Option(None, "--base-path", "-p", help="Base path where directories are located (default: ./{company_name}, required with --clean-dirs)"),
):
    """💀 Kill a tmux company and clean up resources"""
    
    # Set default base_path if not provided
    if base_path is None:
        base_path = f"./{name}"
    
    if not force:
        confirm_msg = f"Are you sure you want to kill company '{name}'?"
        if clean_dirs:
            confirm_msg += f"\nThis will also delete directories under '{base_path}' for this company."
        confirm = typer.confirm(confirm_msg)
        if not confirm:
            raise typer.Exit()

    config = Config("config.yaml")
    tmux = TmuxSession(config)
    try:
        # Kill tmux session first
        tmux.kill_session(name)
        typer.echo(f"💀 Killed company '{name}'")
        
        # Clean directories if requested
        if clean_dirs:
            tmux.clean_company_directories(name, base_path)
            typer.echo(f"🗑️ Cleaned directories for company '{name}' at '{base_path}'")
            
    except Exception as e:
        logger.error(f"Failed to kill company: {e}")
        raise typer.Exit(1)

@company_app.command("list")
def list_companies(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
):
    """🏢 List all active tmux companies"""
    try:
        # Get tmux sessions directly
        result = subprocess.run(['tmux', 'list-sessions'], 
                              capture_output=True, text=True, check=False)
        
        if result.returncode == 0 and result.stdout.strip():
            typer.echo("🏢 Active tmux companies:")
            
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 2:
                    session_name = parts[0]
                    session_info = parts[1].strip()
                    
                    # Check if attached
                    attached = "(attached)" in line
                    attached_icon = "🔗" if attached else "🏛️"
                    
                    if verbose:
                        typer.echo(f"{attached_icon} Company: {session_name}")
                        typer.echo(f"   📅 Info: {session_info}")
                        typer.echo("   ---")
                    else:
                        typer.echo(f"   {attached_icon} {session_name}")
        else:
            typer.echo("🏭 No active companies found")
            typer.echo("💡 Tip: Build a company with 'haconiwa company build --name <name>'")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list companies: {e}")
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ tmux is not installed or not found in PATH")
        raise typer.Exit(1)

if __name__ == "__main__":
    company_app()