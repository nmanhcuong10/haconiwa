from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
import threading
import time

from ..core.config import Config
from .base import BaseAgent

class WorkerSpecialty(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    QA = "qa"

@dataclass
class TaskResult:
    task_id: str
    status: str
    output: Dict[str, Any]
    errors: List[str]
    metrics: Dict[str, float]

class WorkerAgent(BaseAgent):
    def __init__(
        self,
        worker_id: str,
        specialty: WorkerSpecialty,
        config: Config
    ):
        super().__init__(agent_id=worker_id, config=config)
        self.specialty = specialty
        self.current_tasks: Dict[str, Dict] = {}
        self.skill_levels: Dict[str, float] = {}
        self.learning_rate = 0.1
        self._task_lock = threading.Lock()
        self._stop_event = threading.Event()

    async def start(self):
        await super().start()
        self.logger.info(f"Worker {self.agent_id} ({self.specialty.value}) started")
        self._task_processor = asyncio.create_task(self._process_tasks())

    async def stop(self):
        self._stop_event.set()
        if hasattr(self, '_task_processor'):
            await self._task_processor
        await super().stop()

    async def receive_task(self, task: Dict) -> bool:
        if not self._validate_task(task):
            return False

        with self._task_lock:
            task_id = task['id']
            if task_id in self.current_tasks:
                return False
            self.current_tasks[task_id] = task
            return True

    async def report_progress(self, task_id: str, progress: float, metrics: Dict[str, float]):
        if task_id not in self.current_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        await self.send_message(
            "boss",
            {
                "type": "progress",
                "task_id": task_id,
                "progress": progress,
                "metrics": metrics
            }
        )

    async def _process_tasks(self):
        while not self._stop_event.is_set():
            with self._task_lock:
                tasks = list(self.current_tasks.values())

            for task in tasks:
                try:
                    result = await self._execute_task(task)
                    await self._report_result(task['id'], result)
                    self._update_skills(task, result)
                    
                    with self._task_lock:
                        self.current_tasks.pop(task['id'], None)
                
                except Exception as e:
                    self.logger.error(f"Error processing task {task['id']}: {str(e)}")
                    await self._report_error(task['id'], str(e))

            await asyncio.sleep(1)

    async def _execute_task(self, task: Dict) -> TaskResult:
        task_type = task.get('type', '')
        executor = getattr(self, f"_execute_{self.specialty.value}_{task_type}", None)
        
        if not executor:
            raise ValueError(f"Unsupported task type: {task_type} for {self.specialty.value}")

        start_time = time.time()
        result = await executor(task)
        execution_time = time.time() - start_time

        return TaskResult(
            task_id=task['id'],
            status="completed",
            output=result,
            errors=[],
            metrics={"execution_time": execution_time}
        )

    def _validate_task(self, task: Dict) -> bool:
        required_fields = ['id', 'type', 'requirements']
        return all(field in task for field in required_fields)

    async def _report_result(self, task_id: str, result: TaskResult):
        await self.send_message(
            "boss",
            {
                "type": "result",
                "task_id": task_id,
                "result": result.__dict__
            }
        )

    async def _report_error(self, task_id: str, error: str):
        await self.send_message(
            "boss",
            {
                "type": "error",
                "task_id": task_id,
                "error": error
            }
        )

    def _update_skills(self, task: Dict, result: TaskResult):
        if not result.errors:
            skill_key = f"{self.specialty.value}_{task['type']}"
            current_level = self.skill_levels.get(skill_key, 1.0)
            self.skill_levels[skill_key] = min(
                current_level + self.learning_rate,
                5.0
            )

    async def _execute_frontend_task(self, task: Dict) -> Dict:
        raise NotImplementedError

    async def _execute_backend_task(self, task: Dict) -> Dict:
        raise NotImplementedError

    async def _execute_qa_task(self, task: Dict) -> Dict:
        raise NotImplementedError