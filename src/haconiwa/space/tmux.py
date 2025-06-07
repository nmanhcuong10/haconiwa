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
        """Create 4x4 multiagent tmux session with 4 organizations x 4 roles"""
        
        # Default organizations if not provided
        if organizations is None:
            organizations = [
                {"id": "org-01", "name": "動画モデル", "workspace": "video-model-workspace"},
                {"id": "org-02", "name": "リップシンク", "workspace": "lipsync-workspace"},
                {"id": "org-03", "name": "YAML拡張", "workspace": "yaml-enhancement-workspace"},
                {"id": "org-04", "name": "エージェント文書検索", "workspace": "agent-docs-search-workspace"}
            ]
        
        try:
            # Kill existing session if it exists
            self._run_tmux_command(['has-session', '-t', name], check=False)
            if subprocess.run(['tmux', 'has-session', '-t', name], capture_output=True).returncode == 0:
                self._run_tmux_command(['kill-session', '-t', name])
            
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
                    
                    # Create workspace path
                    workspace_path = f"{base_path}/{org['id']}/{org_idx+1:02d}{role}/{org['workspace']}"
                    
                    # Set pane title
                    title = f"{org['id'].upper()}-{role.upper()}-{org['name']}"
                    
                    # Configure pane
                    self._setup_multiagent_pane_subprocess(
                        name, pane_idx, title, workspace_path, org, role
                    )
            
            # Wait a bit then clear all panes
            time.sleep(2)
            for i in range(16):
                self._run_tmux_command(['send-keys', '-t', f'{name}:0.{i}', 'clear', 'C-m'])
            
            # Return session via libtmux
            return self.get_session(name)
            
        except subprocess.CalledProcessError as e:
            raise TmuxSessionError(f"Failed to create multiagent session: {str(e)}")
    
    def _run_tmux_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run tmux command via subprocess"""
        full_cmd = ['tmux'] + cmd
        return subprocess.run(full_cmd, check=check, capture_output=True, text=True)
    
    def _setup_multiagent_pane_subprocess(
        self, 
        session_name: str,
        pane_idx: int, 
        title: str, 
        workspace_path: str, 
        org: Dict[str, str], 
        role: str
    ) -> None:
        """Setup individual pane for multiagent environment using subprocess"""
        try:
            pane_target = f"{session_name}:0.{pane_idx}"
            
            # Set pane title
            self._run_tmux_command(['select-pane', '-t', pane_target, '-T', title])
            
            # Change to workspace directory and show info
            org_name = org['name']
            self._run_tmux_command(['send-keys', '-t', pane_target, 
                                   f"cd {workspace_path} && echo '=== {org['id'].upper()} {role.upper()}: {org_name} ===' && pwd", 'Enter'])
            
            # Set custom prompt
            prompt_prefix = f"({org['id'].upper()}-{role.upper()})"
            self._run_tmux_command(['send-keys', '-t', pane_target, 
                                   f"export PS1='{prompt_prefix} \\$ '", 'C-m'])
            
        except subprocess.CalledProcessError as e:
            # Don't fail the entire session creation for individual pane setup issues
            print(f"Warning: Failed to setup pane {pane_idx}: {e}")

    def attach_session(self, session_name: str) -> None:
        """Attach to an existing tmux session"""
        session = self.get_session(session_name)
        if not session:
            raise TmuxSessionError(f"Session '{session_name}' not found")
        
        try:
            # Use os.execvp to replace current process with tmux attach
            import os
            os.execvp('tmux', ['tmux', 'attach-session', '-t', session_name])
        except Exception as e:
            raise TmuxSessionError(f"Failed to attach to session: {str(e)}")

    def _setup_multiagent_pane(
        self, 
        session: libtmux.Session, 
        pane_idx: int, 
        title: str, 
        workspace_path: str, 
        org: Dict[str, str], 
        role: str
    ) -> None:
        """Setup individual pane for multiagent environment"""
        try:
            window = session.attached_window
            pane = window.get_pane(pane_idx)
            
            # Set pane title
            pane.send_keys(f"printf '\\033]2;{title}\\033\\\\'")
            
            # Change to workspace directory
            pane.send_keys(f"cd {workspace_path}")
            
            # Display organization and role info
            org_name = org['name']
            pane.send_keys(f"echo '=== {org['id'].upper()} {role.upper()}: {org_name} ==='")
            pane.send_keys("pwd")
            
            # Set custom prompt
            prompt_prefix = f"({org['id'].upper()}-{role.upper()})"
            pane.send_keys(f"export PS1='{prompt_prefix} \\$ '")
            
        except Exception as e:
            # Don't fail the entire session creation for individual pane setup issues
            print(f"Warning: Failed to setup pane {pane_idx}: {e}")
