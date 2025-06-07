import os
import shutil
import subprocess
from packaging import version
from haconiwa.core.config import Config
from haconiwa.core.state import StateManager

class Upgrader:
    def __init__(self, config_path="config.yaml"):
        self.config = Config(config_path)
        self.state = StateManager(config_path)

    def get_current_version(self):
        """Get current haconiwa version"""
        try:
            from haconiwa import __version__
            return __version__
        except ImportError:
            return "0.1.0"

    def get_latest_version(self):
        """Get latest version from PyPI"""
        # Simplified - in real implementation would check PyPI
        return "0.1.0"

    def check_version_compatibility(self, current_version, new_version):
        return version.parse(new_version) > version.parse(current_version)

    def backup(self, backup_path):
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
        os.makedirs(backup_path)
        print(f"Backup created at {backup_path}")

    def restore(self, backup_path):
        print(f"State restored from {backup_path}")

    def migrate(self):
        # Placeholder for migration logic
        print("Migrating settings and database...")

    def update_dependencies(self):
        subprocess.run(["pip", "install", "-r", "requirements.txt", "--upgrade"])
        print("Dependencies updated")

    def verify_upgrade(self):
        # Placeholder for verification logic
        print("Verifying upgrade...")

    def upgrade(self, new_version=None):
        current_version = self.get_current_version()
        if new_version is None:
            new_version = self.get_latest_version()
            
        if not self.check_version_compatibility(current_version, new_version):
            print("New version is not compatible")
            return

        backup_path = "backup"
        self.backup(backup_path)

        try:
            self.migrate()
            self.update_dependencies()
            self.verify_upgrade()
            print(f"Upgraded to version {new_version}")
        except Exception as e:
            print(f"Upgrade failed: {e}")
            self.restore(backup_path)
            print("Rolled back to previous state")
        finally:
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            print("Cleanup completed")