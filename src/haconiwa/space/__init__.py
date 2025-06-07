import os

__all__ = ["TmuxManager"]

class TmuxManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, name):
        os.system(f"tmux new-session -d -s {name}")
        self.sessions[name] = True

    def list_sessions(self):
        return os.popen("tmux ls").read().strip()

    def attach_session(self, name):
        os.system(f"tmux attach-session -t {name}")

    def kill_session(self, name):
        os.system(f"tmux kill-session -t {name}")
        del self.sessions[name]