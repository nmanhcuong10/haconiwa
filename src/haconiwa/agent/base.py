from abc import ABC, abstractmethod
import asyncio
import threading
import time
from typing import Any, Dict, Optional

from ..core.config import Config
from ..core.logging import get_logger

class BaseAgent(ABC):
    def __init__(self, agent_id: str, config: Config):
        self.agent_id = agent_id
        self.config = config
        self.logger = get_logger(f"agent.{agent_id}")
        self.state: Dict[str, Any] = {}
        self._running = False
        self._lock = threading.Lock()
        self._metrics: Dict[str, float] = {}
        self._plugins: Dict[str, Any] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()

    async def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            self.logger.info(f"Starting agent {self.agent_id}")
            await self._initialize()
            asyncio.create_task(self._run_loop())
            asyncio.create_task(self._monitor_metrics())

    async def stop(self):
        with self._lock:
            if not self._running:
                return
            self._running = False
            self.logger.info(f"Stopping agent {self.agent_id}")
            await self._cleanup()

    async def send_message(self, message: Dict[str, Any]):
        await self._message_queue.put(message)
        self._update_metric("messages_sent", 1)

    def register_plugin(self, name: str, plugin: Any):
        if name in self._plugins:
            raise ValueError(f"Plugin {name} already registered")
        self._plugins[name] = plugin
        self.logger.info(f"Registered plugin: {name}")

    def get_metric(self, name: str) -> float:
        return self._metrics.get(name, 0.0)

    @abstractmethod
    async def _initialize(self):
        pass

    @abstractmethod
    async def _process_message(self, message: Dict[str, Any]):
        pass

    @abstractmethod
    async def _cleanup(self):
        pass

    async def _run_loop(self):
        try:
            while self._running:
                message = await self._message_queue.get()
                start_time = time.time()
                try:
                    await self._process_message(message)
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    self._update_metric("message_errors", 1)
                finally:
                    processing_time = time.time() - start_time
                    self._update_metric("message_processing_time", processing_time)
                    self._message_queue.task_done()
        except Exception as e:
            self.logger.error(f"Agent run loop error: {e}")
            self._running = False

    async def _monitor_metrics(self):
        while self._running:
            self._update_metric("queue_size", self._message_queue.qsize())
            self._update_metric("uptime", time.time() - self._start_time)
            await asyncio.sleep(self.config.get("metrics_interval", 60))

    def _update_metric(self, name: str, value: float):
        with self._lock:
            self._metrics[name] = value

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def plugins(self) -> Dict[str, Any]:
        return self._plugins.copy()

    @property
    def metrics(self) -> Dict[str, float]:
        return self._metrics.copy()