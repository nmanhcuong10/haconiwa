"""
Path Scanner for Haconiwa v1.0
"""

import os
import pathlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from fnmatch import fnmatch
from typing import Dict, List, Optional, Set, Any
import logging

from ..core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class FileMetadata:
    path: str
    size: int
    modified: datetime
    mode: int
    is_dir: bool


class PathScanner:
    """File path scanner with include/exclude patterns"""
    
    _configs = {}
    
    def __init__(self):
        pass
    
    @classmethod
    def register_config(cls, name: str, config: Dict[str, Any]):
        """Register PathScan configuration"""
        cls._configs[name] = config
        logger.info(f"Registered PathScan config: {name}")
    
    def scan(self, config_name: str) -> List[str]:
        """Scan files using configuration"""
        config = self._configs.get(config_name)
        if not config:
            logger.error(f"PathScan config not found: {config_name}")
            return []
        
        # Mock implementation - would use actual file scanning
        include_patterns = config.get("include", [])
        exclude_patterns = config.get("exclude", [])
        
        logger.info(f"Scanning with patterns - include: {include_patterns}, exclude: {exclude_patterns}")
        
        # Return mock results
        return ["src/main.py", "src/utils.py", "src/config.py"]

    def _load_gitignore(self, config: Config):
        gitignore_path = pathlib.Path(".gitignore")
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                config.ignore_patterns = {line.strip() for line in f if line.strip() and not line.startswith("#")}

    def _should_ignore(self, path: str, config: Config) -> bool:
        path_parts = pathlib.Path(path).parts
        return any(
            any(fnmatch(part, pattern) for part in path_parts)
            for pattern in config.ignore_patterns
        )

    def _get_metadata(self, path: pathlib.Path) -> FileMetadata:
        stat = path.stat()
        return FileMetadata(
            path=str(path),
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
            mode=stat.st_mode,
            is_dir=path.is_dir()
        )

    def _scan_directory(self, directory: pathlib.Path, config: Config) -> List[FileMetadata]:
        results = []
        try:
            for entry in directory.iterdir():
                if self._should_ignore(str(entry), config):
                    continue
                metadata = self._get_metadata(entry)
                results.append(metadata)
                if metadata.is_dir:
                    results.extend(self._scan_directory(entry, config))
        except PermissionError:
            pass
        return results

    def scan_with_config(self, root_path: str, config_name: str, pattern: Optional[str] = None, parallel: bool = True) -> List[FileMetadata]:
        config = self._configs.get(config_name)
        if not config:
            logger.error(f"PathScan config not found: {config_name}")
            return []
        
        root = pathlib.Path(root_path)
        if not root.exists():
            return []

        if not parallel:
            results = self._scan_directory(root, config)
        else:
            with ThreadPoolExecutor() as executor:
                first_level = [d for d in root.iterdir() if d.is_dir() and not self._should_ignore(str(d), config)]
                results = []
                for subdir_results in executor.map(self._scan_directory, first_level, [config] * len(first_level)):
                    results.extend(subdir_results)

        if pattern:
            results = [r for r in results if fnmatch(r.path, pattern)]

        return results

    def get_changes(self, root_path: str, config_name: str) -> Dict[str, List[FileMetadata]]:
        current_files = {m.path: m for m in self.scan_with_config(root_path, config_name, parallel=False)}
        
        added = []
        modified = []
        removed = []

        for path, metadata in current_files.items():
            if path not in self._configs[config_name]["cache"]:
                added.append(metadata)
            elif self._configs[config_name]["cache"][path].modified != metadata.modified:
                modified.append(metadata)

        removed = [
            self._configs[config_name]["cache"][path] for path in self._configs[config_name]["cache"]
            if path.startswith(root_path) and path not in current_files
        ]

        return {
            "added": added,
            "modified": modified,
            "removed": removed
        }

    def clear_cache(self, config_name: str):
        self._configs[config_name]["cache"].clear()