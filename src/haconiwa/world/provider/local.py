import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from haconiwa.core.config import Config


class LocalProvider:
    def __init__(self, config: Config):
        self.config = config
        self.root_dir = Path(config.get("worlds.root_dir", "worlds"))
        self.current_world: Optional[str] = None

    def create_world(self, world_id: str, options: Dict = None) -> bool:
        world_path = self.root_dir / world_id
        if world_path.exists():
            return False

        try:
            world_path.mkdir(parents=True)
            (world_path / "state").mkdir()
            (world_path / "tmp").mkdir()
            
            env_file = world_path / ".env"
            env_file.write_text(self._generate_env_content(world_id, options))
            
            self._setup_permissions(world_path)
            self._create_backup_dir(world_path)
            
            self.current_world = world_id
            return True
        except Exception:
            if world_path.exists():
                shutil.rmtree(world_path)
            return False

    def destroy_world(self, world_id: str) -> bool:
        world_path = self.root_dir / world_id
        if not world_path.exists():
            return False

        try:
            self._cleanup_processes(world_id)
            shutil.rmtree(world_path)
            if self.current_world == world_id:
                self.current_world = None
            return True
        except Exception:
            return False

    def enter_world(self, world_id: str) -> bool:
        world_path = self.root_dir / world_id
        if not world_path.exists():
            return False

        try:
            os.chdir(world_path)
            self.current_world = world_id
            self._load_env_file(world_path / ".env")
            return True
        except Exception:
            return False

    def list_worlds(self) -> List[str]:
        return [d.name for d in self.root_dir.iterdir() if d.is_dir()]

    def backup_world(self, world_id: str, backup_name: str) -> bool:
        world_path = self.root_dir / world_id
        backup_path = world_path / "backups" / backup_name

        if not world_path.exists() or backup_path.exists():
            return False

        try:
            shutil.copytree(world_path / "state", backup_path)
            return True
        except Exception:
            return False

    def restore_world(self, world_id: str, backup_name: str) -> bool:
        world_path = self.root_dir / world_id
        backup_path = world_path / "backups" / backup_name
        state_path = world_path / "state"

        if not backup_path.exists():
            return False

        try:
            if state_path.exists():
                shutil.rmtree(state_path)
            shutil.copytree(backup_path, state_path)
            return True
        except Exception:
            return False

    def _generate_env_content(self, world_id: str, options: Optional[Dict] = None) -> str:
        env_vars = {
            "WORLD_ID": world_id,
            "WORLD_PATH": str(self.root_dir / world_id),
            "PYTHONPATH": os.getenv("PYTHONPATH", ""),
            "PATH": os.getenv("PATH", "")
        }
        
        if options:
            env_vars.update(options)
            
        return "\n".join(f"{k}={v}" for k, v in env_vars.items())

    def _setup_permissions(self, world_path: Path) -> None:
        world_path.chmod(0o755)
        (world_path / "state").chmod(0o755)
        (world_path / "tmp").chmod(0o755)

    def _create_backup_dir(self, world_path: Path) -> None:
        backup_dir = world_path / "backups"
        backup_dir.mkdir()
        backup_dir.chmod(0o755)

    def _cleanup_processes(self, world_id: str) -> None:
        try:
            subprocess.run(["pkill", "-f", f"world_id={world_id}"], check=False)
        except Exception:
            pass

    def _load_env_file(self, env_file: Path) -> None:
        if not env_file.exists():
            return

        content = env_file.read_text()
        for line in content.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()