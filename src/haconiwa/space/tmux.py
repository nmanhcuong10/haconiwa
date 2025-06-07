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
