import os
import time
import subprocess
import libtmux
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from haconiwa.core.config import Config

class TmuxSessionError(Exception):
    pass

class TmuxSession:
    def __init__(self, config: Config):
        self.config = config
        self.server = libtmux.Server()
        self._validate_tmux()

    def _validate_tmux(self) -> None:
        try:
            subprocess.run(['tmux', '-V'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise TmuxSessionError("tmux is not installed or not accessible")

    def create_session(self, name: str, window_name: str = 'main') -> libtmux.Session:
        try:
            if self.server.has_session(name):
                raise TmuxSessionError(f"Session '{name}' already exists")
            
            session = self.server.new_session(
                session_name=name,
                window_name=window_name,
                attach=False
            )
            return session
        except libtmux.exc.TmuxCommandError as e:
            raise TmuxSessionError(f"Failed to create session: {str(e)}")

    def get_session(self, name: str) -> Optional[libtmux.Session]:
        try:
            return self.server.find_where({'session_name': name})
        except libtmux.exc.TmuxCommandError:
            return None

    def list_sessions(self) -> List[Dict[str, str]]:
        sessions = []
        for session in self.server.list_sessions():
            sessions.append({
                'name': session.name,
                'created': session.get('session_created'),
                'windows': len(session.list_windows()),
                'attached': session.attached
            })
        return sessions

    def split_window(self, session_name: str, layout: str = 'even-horizontal') -> None:
        session = self.get_session(session_name)
        if not session:
            raise TmuxSessionError(f"Session '{session_name}' not found")

        try:
            window = session.attached_window
            window.split_window()
            window.select_layout(layout)
        except libtmux.exc.TmuxCommandError as e:
            raise TmuxSessionError(f"Failed to split window: {str(e)}")

    def send_command(self, session_name: str, command: str, pane_id: Optional[int] = None) -> None:
        session = self.get_session(session_name)
        if not session:
            raise TmuxSessionError(f"Session '{session_name}' not found")

        try:
            if pane_id is not None:
                pane = session.attached_window.get_pane(pane_id)
            else:
                pane = session.attached_window.attached_pane
            
            pane.send_keys(command)
        except libtmux.exc.TmuxCommandError as e:
            raise TmuxSessionError(f"Failed to send command: {str(e)}")

    def capture_pane(self, session_name: str, pane_id: Optional[int] = None) -> str:
        session = self.get_session(session_name)
        if not session:
            raise TmuxSessionError(f"Session '{session_name}' not found")

        try:
            if pane_id is not None:
                pane = session.attached_window.get_pane(pane_id)
            else:
                pane = session.attached_window.attached_pane
            
            return pane.capture_pane()
        except libtmux.exc.TmuxCommandError as e:
            raise TmuxSessionError(f"Failed to capture pane: {str(e)}")

    def kill_session(self, session_name: str) -> None:
        session = self.get_session(session_name)
        if not session:
            raise TmuxSessionError(f"Session '{session_name}' not found")

        try:
            session.kill_session()
        except libtmux.exc.TmuxCommandError as e:
            raise TmuxSessionError(f"Failed to kill session: {str(e)}")

    def resize_pane(self, session_name: str, pane_id: int, height: Optional[int] = None, width: Optional[int] = None) -> None:
        session = self.get_session(session_name)
        if not session:
            raise TmuxSessionError(f"Session '{session_name}' not found")

        try:
            pane = session.attached_window.get_pane(pane_id)
            if height:
                pane.resize_pane(height=height)
            if width:
                pane.resize_pane(width=width)
        except libtmux.exc.TmuxCommandError as e:
            raise TmuxSessionError(f"Failed to resize pane: {str(e)}")

    def is_session_alive(self, session_name: str) -> bool:
        return self.get_session(session_name) is not None

    def wait_until_ready(self, session_name: str, timeout: int = 10) -> None:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_session_alive(session_name):
                return
            time.sleep(0.1)
        raise TmuxSessionError(f"Session '{session_name}' failed to start within {timeout} seconds")

    def load_layout(self, session_name: str, layout_file: Path) -> None:
        if not layout_file.exists():
            raise TmuxSessionError(f"Layout file '{layout_file}' not found")

        session = self.get_session(session_name)
        if not session:
            raise TmuxSessionError(f"Session '{session_name}' not found")

        try:
            with layout_file.open() as f:
                layout_commands = f.read().splitlines()
            
            for cmd in layout_commands:
                if cmd.strip() and not cmd.startswith('#'):
                    self.send_command(session_name, cmd)
                    time.sleep(0.1)
        except Exception as e:
            raise TmuxSessionError(f"Failed to load layout: {str(e)}")

    def save_layout(self, session_name: str, layout_file: Path) -> None:
        session = self.get_session(session_name)
        if not session:
            raise TmuxSessionError(f"Session '{session_name}' not found")

        try:
            window = session.attached_window
            layout = window.layout
            
            layout_file.parent.mkdir(parents=True, exist_ok=True)
            layout_file.write_text(layout)
        except Exception as e:
            raise TmuxSessionError(f"Failed to save layout: {str(e)}")

    def create_multiagent_session(
        self, 
        name: str, 
        base_path: str,
        organizations: Optional[List[Dict[str, str]]] = None
    ) -> libtmux.Session:
        """Create 4x4 multiagent tmux company with 4 organizations x 4 roles"""
        
        # Default organizations if not provided
        if organizations is None:
            organizations = [
                {"id": "org-01", "org_name": "", "task_name": "", "workspace": "video-model-desk"},
                {"id": "org-02", "org_name": "", "task_name": "", "workspace": "lipsync-desk"},
                {"id": "org-03", "org_name": "", "task_name": "", "workspace": "yaml-enhancement-desk"},
                {"id": "org-04", "org_name": "", "task_name": "", "workspace": "agent-docs-search-desk"}
            ]
        
        # Check if session already exists
        existing_session = self.get_session(name)
        if existing_session:
            print(f"🔄 Updating existing company '{name}'...")
            return self._update_existing_session(name, base_path, organizations)
        
        # Create directory structure
        self._create_directory_structure(base_path, organizations, company_name=name)
        
        try:
            # Create new session
            self._run_tmux_command(['new-session', '-d', '-s', name])
            
            # Load tmux config
            self._run_tmux_command(['source-file', '~/.tmux.conf'], check=False)
            
            # Rename first window
            self._run_tmux_command(['rename-window', '-t', f'{name}:0', 'multiagent'])
            
            # Create 4x4 pane layout (16 panes total)
            # Split vertically 3 times to create 4 rows
            self._run_tmux_command(['split-window', '-v', '-t', f'{name}:0.0'])
            self._run_tmux_command(['split-window', '-v', '-t', f'{name}:0.0'])  
            self._run_tmux_command(['split-window', '-v', '-t', f'{name}:0.1'])
            
            # Split each row horizontally 3 times to create 4 columns
            # Row 1 (panes 0-3)
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.0'])
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.0'])
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.1'])
            
            # Row 2 (panes 4-7)
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.4'])
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.4'])
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.5'])
            
            # Row 3 (panes 8-11)
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.8'])
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.8'])
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.9'])
            
            # Row 4 (panes 12-15)
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.12'])
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.12'])
            self._run_tmux_command(['split-window', '-h', '-t', f'{name}:0.13'])
            
            # Apply tiled layout for even distribution
            self._run_tmux_command(['select-layout', '-t', f'{name}:0', 'tiled'])
            
            # Configure pane borders and titles
            self._run_tmux_command(['set-option', '-t', name, 'pane-border-status', 'top'])
            self._run_tmux_command(['set-option', '-t', name, 'pane-border-format', '#{pane_title}'])
            
            # Setup each pane with organization and role
            roles = ['boss', 'worker-a', 'worker-b', 'worker-c']
            
            for org_idx, org in enumerate(organizations):
                for role_idx, role in enumerate(roles):
                    pane_idx = org_idx * 4 + role_idx
                    
                    # Create desk path based on new directory structure
                    role_dir = f"{org_idx+1:02d}{role}"  # e.g., "01boss", "01worker-a"
                    desk_path = f"{base_path}/{org['id']}/{role_dir}"
                    
                    # Set pane title with organization name and/or task name
                    title_parts = []
                    
                    # Start with organization name (or org-id if no name)
                    if org['org_name']:
                        title_parts.append(org['org_name'])
                    else:
                        title_parts.append(org['id'].upper())
                    
                    # Add role
                    title_parts.append(role.upper())
                    
                    # Add task name if specified
                    if org['task_name']:
                        title_parts.append(org['task_name'])
                    
                    title = "-".join(title_parts)
                    
                    # Configure pane
                    self._setup_multiagent_pane_subprocess(
                        name, pane_idx, title, desk_path, org, role
                    )
            
            # Wait a bit then clear all panes
            time.sleep(2)
            for i in range(16):
                self._run_tmux_command(['send-keys', '-t', f'{name}:0.{i}', 'clear', 'C-m'])
            
            # Return session via libtmux
            return self.get_session(name)
            
        except subprocess.CalledProcessError as e:
            raise TmuxSessionError(f"Failed to create multiagent company: {str(e)}")
    
    def _update_existing_session(
        self,
        name: str,
        base_path: str,
        organizations: List[Dict[str, str]]
    ) -> libtmux.Session:
        """Update existing company pane titles without recreating the company"""
        try:
            # Create any missing directories (but don't overwrite existing ones)
            self._create_directory_structure(base_path, organizations, update_mode=True, company_name=name)
            
            # Update pane titles only
            roles = ['boss', 'worker-a', 'worker-b', 'worker-c']
            
            for org_idx, org in enumerate(organizations):
                for role_idx, role in enumerate(roles):
                    pane_idx = org_idx * 4 + role_idx
                    
                    # Generate new title
                    title_parts = []
                    
                    # Start with organization name (or org-id if no name)
                    if org['org_name']:
                        title_parts.append(org['org_name'])
                    else:
                        title_parts.append(org['id'].upper())
                    
                    # Add role
                    title_parts.append(role.upper())
                    
                    # Add task name if specified
                    if org['task_name']:
                        title_parts.append(org['task_name'])
                    
                    title = "-".join(title_parts)
                    
                    # Update pane title only
                    pane_target = f"{name}:0.{pane_idx}"
                    self._run_tmux_command(['select-pane', '-t', pane_target, '-T', title])
            
            print(f"✅ Updated pane titles for company '{name}'")
            return self.get_session(name)
            
        except subprocess.CalledProcessError as e:
            raise TmuxSessionError(f"Failed to update company: {str(e)}")
    
    def _create_directory_structure(self, base_path: str, organizations: List[Dict[str, str]], update_mode: bool = False, company_name: str = "default") -> None:
        """Create directory structure for multiagent environment"""
        try:
            # Create base path if it doesn't exist
            base_path_obj = Path(base_path)
            base_path_obj.mkdir(parents=True, exist_ok=True)
            
            roles = ['boss', 'worker-a', 'worker-b', 'worker-c']
            created_directories = []
            
            for org_idx, org in enumerate(organizations):
                # Create organization directory
                org_path = base_path_obj / org['id']
                org_path.mkdir(exist_ok=True)
                created_directories.append(org['id'])
                
                # Create role directories (desks)
                for role in roles:
                    role_dir = f"{org_idx+1:02d}{role}"  # e.g., "01boss", "01worker-a"
                    role_path = org_path / role_dir
                    role_path.mkdir(exist_ok=True)
                    
                    # Create a simple README in each directory (but don't overwrite in update mode)
                    readme_path = role_path / "README.md"
                    if not readme_path.exists() or not update_mode:
                        org_info = f"\n## 組織: {org['org_name']}" if org['org_name'] else ""
                        task_info = f"\n## タスク: {org['task_name']}" if org['task_name'] else ""
                        
                        readme_content = f"""# {org['id'].upper()} - {role.upper()}{org_info}{task_info}

## 役割: {role}

このディレクトリは {org['id'].upper()} の {role} 用のデスクです。

### 使用方法
- このデスクでプロジェクトの作業を行ってください
- 各役割に応じたタスクを管理してください
- 他の組織・役割との連携を意識してください

### 生成日時
{time.strftime('%Y-%m-%d %H:%M:%S')}
"""
                        readme_path.write_text(readme_content, encoding='utf-8')
            
            # Create metadata file for cleanup tracking (only if not in update mode)
            if not update_mode:
                self._create_company_metadata(base_path_obj, created_directories, company_name)
                        
        except Exception as e:
            if update_mode:
                print(f"Warning: Failed to update directory structure: {e}")
            else:
                print(f"Warning: Failed to create directory structure: {e}")
    
    def _create_company_metadata(self, base_path_obj: Path, directories: List[str], company_name: str = "default") -> None:
        """Create metadata file for tracking created directories"""
        try:
            import json
            
            # Use company-specific metadata filename for easier cleanup
            metadata_file = base_path_obj / f".haconiwa-{company_name}.json"
            
            metadata = {
                "company_name": company_name,
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "directories": directories,
                "base_path": str(base_path_obj)
            }
            
            with metadata_file.open('w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Failed to create metadata file: {e}")

    def _run_tmux_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run tmux command via subprocess"""
        full_cmd = ['tmux'] + cmd
        return subprocess.run(full_cmd, check=check, capture_output=True, text=True)
    
    def _setup_multiagent_pane_subprocess(
        self, 
        session_name: str,
        pane_idx: int, 
        title: str, 
        desk_path: str, 
        org: Dict[str, str], 
        role: str
    ) -> None:
        """Setup individual pane for multiagent environment using subprocess"""
        try:
            pane_target = f"{session_name}:0.{pane_idx}"
            
            # Set pane title
            self._run_tmux_command(['select-pane', '-t', pane_target, '-T', title])
            
            # Change to desk directory and show info
            display_parts = [f"{org['id'].upper()} {role.upper()}"]
            if org['org_name']:
                display_parts.append(f"組織: {org['org_name']}")
            if org['task_name']:
                display_parts.append(f"タスク: {org['task_name']}")
            display_text = " - ".join(display_parts)
            
            self._run_tmux_command(['send-keys', '-t', pane_target, 
                                   f"cd {desk_path} && echo '=== {display_text} ===' && pwd", 'Enter'])
            
            # Set custom prompt
            prompt_prefix = f"({org['id'].upper()}-{role.upper()})"
            self._run_tmux_command(['send-keys', '-t', pane_target, 
                                   f"export PS1='{prompt_prefix} \\$ '", 'C-m'])
            
        except subprocess.CalledProcessError as e:
            # Don't fail the entire session creation for individual pane setup issues
            print(f"Warning: Failed to setup pane {pane_idx}: {e}")

    def attach_session(self, session_name: str) -> None:
        """Attach to an existing tmux company"""
        session = self.get_session(session_name)
        if not session:
            raise TmuxSessionError(f"Company '{session_name}' not found")
        
        try:
            # Use os.execvp to replace current process with tmux attach
            import os
            os.execvp('tmux', ['tmux', 'attach-session', '-t', session_name])
        except Exception as e:
            raise TmuxSessionError(f"Failed to attach to company: {str(e)}")

    def clean_company_directories(self, company_name: str, base_path: str) -> None:
        """Clean directories created for a company"""
        try:
            import shutil
            base_path_obj = Path(base_path)
            
            if not base_path_obj.exists():
                print(f"Base path '{base_path}' does not exist, nothing to clean")
                return
            
            # Look for company metadata file first
            metadata_file = base_path_obj / f".haconiwa-{company_name}.json"
            if metadata_file.exists():
                # If metadata exists, use it to determine what to clean
                try:
                    import json
                    with metadata_file.open('r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Remove directories listed in metadata
                    for org_dir in metadata.get('directories', []):
                        org_path = base_path_obj / org_dir
                        if org_path.exists() and org_path.is_dir():
                            shutil.rmtree(org_path)
                            print(f"Removed directory: {org_path}")
                    
                    # Remove metadata file
                    metadata_file.unlink()
                    print(f"Removed metadata file: {metadata_file}")
                    
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Warning: Failed to read metadata file: {e}")
                    # Fallback to default cleanup
                    self._clean_default_directories(base_path_obj)
            else:
                # No metadata file, use default organization structure
                self._clean_default_directories(base_path_obj)
            
            # Remove base directory if it's empty
            try:
                if base_path_obj.exists() and not any(base_path_obj.iterdir()):
                    base_path_obj.rmdir()
                    print(f"Removed empty base directory: {base_path_obj}")
            except OSError:
                # Directory not empty, that's fine
                pass
                
        except Exception as e:
            print(f"Warning: Failed to clean directories: {e}")
    
    def _clean_default_directories(self, base_path_obj: Path) -> None:
        """Clean default organization directories (org-01 to org-04)"""
        import shutil
        
        for org_id in ['org-01', 'org-02', 'org-03', 'org-04']:
            org_path = base_path_obj / org_id
            if org_path.exists() and org_path.is_dir():
                shutil.rmtree(org_path)
                print(f"Removed directory: {org_path}")
