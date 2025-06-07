import os
import pathlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from fnmatch import fnmatch
from typing import Dict, List, Optional, Set

from ..core.config import Config


@dataclass
class FileMetadata:
    path: str
    size: int
    modified: datetime
    mode: int
    is_dir: bool


class PathScanner:
    def __init__(self, config: Config):
        self.config = config
        self.cache: Dict[str, FileMetadata] = {}
        self.ignore_patterns: Set[str] = set()
        self._load_gitignore()

    def _load_gitignore(self):
        gitignore_path = pathlib.Path(".gitignore")
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                self.ignore_patterns = {line.strip() for line in f if line.strip() and not line.startswith("#")}

    def _should_ignore(self, path: str) -> bool:
        path_parts = pathlib.Path(path).parts
        return any(
            any(fnmatch(part, pattern) for part in path_parts)
            for pattern in self.ignore_patterns
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

    def _scan_directory(self, directory: pathlib.Path) -> List[FileMetadata]:
        results = []
        try:
            for entry in directory.iterdir():
                if self._should_ignore(str(entry)):
                    continue
                metadata = self._get_metadata(entry)
                self.cache[str(entry)] = metadata
                results.append(metadata)
                if metadata.is_dir:
                    results.extend(self._scan_directory(entry))
        except PermissionError:
            pass
        return results

    def scan(self, root_path: str, pattern: Optional[str] = None, parallel: bool = True) -> List[FileMetadata]:
        root = pathlib.Path(root_path)
        if not root.exists():
            return []

        if not parallel:
            results = self._scan_directory(root)
        else:
            with ThreadPoolExecutor() as executor:
                first_level = [d for d in root.iterdir() if d.is_dir() and not self._should_ignore(str(d))]
                results = []
                for subdir_results in executor.map(self._scan_directory, first_level):
                    results.extend(subdir_results)

        if pattern:
            results = [r for r in results if fnmatch(r.path, pattern)]

        return results

    def get_changes(self, root_path: str) -> Dict[str, List[FileMetadata]]:
        current_files = {m.path: m for m in self.scan(root_path, parallel=False)}
        
        added = []
        modified = []
        removed = []

        for path, metadata in current_files.items():
            if path not in self.cache:
                added.append(metadata)
            elif self.cache[path].modified != metadata.modified:
                modified.append(metadata)

        removed = [
            self.cache[path] for path in self.cache
            if path.startswith(root_path) and path not in current_files
        ]

        return {
            "added": added,
            "modified": modified,
            "removed": removed
        }

    def clear_cache(self):
        self.cache.clear()