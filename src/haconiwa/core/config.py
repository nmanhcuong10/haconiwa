import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, validator
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cryptography.fernet import Fernet

class SecuritySettings(BaseModel):
    encryption_key: Optional[str] = None
    access_control: Dict[str, list] = Field(default_factory=dict)

class GlobalSettings(BaseModel):
    debug: bool = False
    log_level: str = "INFO"
    security: SecuritySettings = Field(default_factory=SecuritySettings)

class OrganizationSettings(BaseModel):
    org_id: str
    boss_model: str = "gpt-4"
    worker_models: Dict[str, str] = Field(default_factory=dict)
    task_rules: Dict[str, Any] = Field(default_factory=dict)

class Config:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.global_config = GlobalSettings()
        self.org_configs: Dict[str, OrganizationSettings] = {}
        self._fernet = None
        self._observer = None
        self._load_config()
        self._setup_hot_reload()

    def _load_config(self) -> None:
        if not self.config_path.exists():
            return

        with open(self.config_path) as f:
            config_data = yaml.safe_load(f)

        if self._fernet and config_data.get("encrypted"):
            config_data = yaml.safe_load(
                self._fernet.decrypt(config_data["data"].encode()).decode()
            )

        self.global_config = GlobalSettings(**config_data.get("global", {}))
        
        for org_id, org_data in config_data.get("organizations", {}).items():
            self.org_configs[org_id] = OrganizationSettings(
                org_id=org_id, **org_data
            )

    def _setup_hot_reload(self) -> None:
        config_path = self.config_path
        load_config = self._load_config
        
        class ConfigFileHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path == str(config_path):
                    load_config()

        self._observer = Observer()
        self._observer.schedule(
            ConfigFileHandler(), str(self.config_path.parent), recursive=False
        )
        self._observer.start()

    def get_org_config(self, org_id: str) -> Optional[OrganizationSettings]:
        return self.org_configs.get(org_id)

    def update_org_config(self, org_id: str, **updates) -> None:
        if org_id not in self.org_configs:
            self.org_configs[org_id] = OrganizationSettings(org_id=org_id)
        
        current_config = self.org_configs[org_id].dict()
        current_config.update(updates)
        self.org_configs[org_id] = OrganizationSettings(**current_config)
        self._save_config()

    def enable_encryption(self, key: Optional[str] = None) -> None:
        if not key:
            key = Fernet.generate_key()
        self._fernet = Fernet(key)
        self.global_config.security.encryption_key = key.decode()
        self._save_config()

    def _save_config(self) -> None:
        config_data = {
            "global": self.global_config.dict(),
            "organizations": {
                org_id: config.dict() 
                for org_id, config in self.org_configs.items()
            }
        }

        if self._fernet:
            encrypted_data = self._fernet.encrypt(
                yaml.dump(config_data).encode()
            ).decode()
            config_data = {
                "encrypted": True,
                "data": encrypted_data
            }

        with open(self.config_path, "w") as f:
            yaml.dump(config_data, f)

    def __del__(self):
        if self._observer:
            self._observer.stop()
            self._observer.join();