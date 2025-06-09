"""
Task Manager for Haconiwa v1.0
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TaskManager:
    """Task manager for Git worktree tasks"""
    
    def __init__(self):
        self.tasks = {}
    
    def create_task(self, config: Dict[str, Any]) -> bool:
        """Create task from configuration"""
        try:
            name = config.get("name")
            branch = config.get("branch")
            worktree = config.get("worktree", True)
            assignee = config.get("assignee")
            
            self.tasks[name] = {
                "config": config,
                "status": "created"
            }
            
            logger.info(f"Created task: {name} (branch: {branch}, assignee: {assignee})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return False 