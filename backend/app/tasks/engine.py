import logging
from typing import Any
from app.tasks.repository import TaskRepository
from app.services.supabase import is_memory_enabled

logger = logging.getLogger(__name__)


class TaskEngine:
    def __init__(self) -> None:
        self.repository = TaskRepository()
        self.enabled = is_memory_enabled()

    async def create_task(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {}
        
        try:
            data["status"] = "pending"
            return await self.repository.create(data)
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return {}

    async def list_tasks(self, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        
        try:
            return await self.repository.list(status, limit)
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return []

    async def get_task(self, task_id: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        
        try:
            return await self.repository.get(task_id)
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None

    async def update_task(self, task_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        
        try:
            return await self.repository.update(task_id, data)
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return None

    async def complete_task(self, task_id: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        
        try:
            return await self.repository.update(task_id, {"status": "done"})
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return None

    async def delete_task(self, task_id: str) -> bool:
        if not self.enabled:
            return False
        
        try:
            return await self.repository.delete(task_id)
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return False