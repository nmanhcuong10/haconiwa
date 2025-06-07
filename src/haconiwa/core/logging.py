import json
import logging
import logging.handlers
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.config import Config

class haconiwaLogger:
    def __init__(self, name: str, config: Config):
        self.name = name
        self.config = config
        self.logger = self._setup_logger()
        self._setup_handlers()
        self._setup_formatters()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        logger.setLevel(self.config.get("logging.level", logging.INFO))
        return logger

    def _setup_handlers(self):
        log_dir = Path(self.config.get("logging.directory", "logs"))
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.name}.log",
            maxBytes=self.config.get("logging.max_bytes", 10_000_000),
            backupCount=self.config.get("logging.backup_count", 5)
        )
        self.logger.addHandler(file_handler)

        if self.config.get("logging.console_output", True):
            console_handler = logging.StreamHandler()
            self.logger.addHandler(console_handler)

    def _setup_formatters(self):
        json_formatter = logging.Formatter(
            lambda x: json.dumps({
                'timestamp': datetime.fromtimestamp(x.created).isoformat(),
                'name': x.name,
                'level': x.levelname,
                'message': x.getMessage(),
                'extra': x.__dict__.get('extra', {}),
                'exception': x.exc_info[1].__str__() if x.exc_info else None
            }, default=str)
        )

        for handler in self.logger.handlers:
            handler.setFormatter(json_formatter)

    def _log(self, level: int, msg: str, extra: Optional[Dict[str, Any]] = None):
        extra = extra or {}
        extra.update({
            'process_id': os.getpid(),
            'thread_id': time.thread_time_ns(),
            'performance': {
                'cpu_percent': self.get_cpu_usage(),
                'memory_usage': self.get_memory_usage()
            }
        })
        self.logger.log(level, msg, extra=extra)

    def debug(self, msg: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.DEBUG, msg, extra)

    def info(self, msg: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.INFO, msg, extra)

    def warning(self, msg: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.WARNING, msg, extra)

    def error(self, msg: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.ERROR, msg, extra)

    def critical(self, msg: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.CRITICAL, msg, extra)

    def get_cpu_usage(self) -> float:
        try:
            import psutil
            return psutil.Process().cpu_percent()
        except ImportError:
            return 0.0

    def get_memory_usage(self) -> Dict[str, int]:
        try:
            import psutil
            process = psutil.Process()
            return {
                'rss': process.memory_info().rss,
                'vms': process.memory_info().vms
            }
        except ImportError:
            return {'rss': 0, 'vms': 0}

    def rotate_logs(self):
        for handler in self.logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.doRollover()

    def archive_logs(self, archive_dir: Optional[str] = None):
        if not archive_dir:
            archive_dir = self.config.get("logging.archive_directory", "logs/archive")
        
        archive_path = Path(archive_dir)
        archive_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for handler in self.logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                log_path = Path(handler.baseFilename)
                if log_path.exists():
                    archive_file = archive_path / f"{log_path.stem}_{timestamp}{log_path.suffix}"
                    log_path.rename(archive_file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.error(f"Exception occurred: {exc_val}", {'exception_type': exc_type.__name__})
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)

def setup_logging(log_level: str = "INFO") -> None:
    """Set up basic logging configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)