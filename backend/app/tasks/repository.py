from __future__ import annotations
import logging
from typing import Any
from app.services.supabase import get_supabase_client
from app.tasks.errors import TaskError

logger = logging.getLogger(__name__)


class TaskRepository:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            raise TaskError("Supabase not configured")
        
        result = self.client.table("tasks").insert(data).execute()
        return result.data[0] if result.data else {}

    async def get(self, task_id: str) -> dict[str, Any] | None:
        if self.client is None:
            return None
        
        result = self.client.table("tasks").select("*").eq("id", task_id).execute()
        return result.data[0] if result.data else None

    async def list(self, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        
        query = self.client.table("tasks").select("*")
        
        if status:
            query = query.eq("status", status)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        return result.data or []

    async def update(self, task_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        if self.client is None:
            return None
        
        result = self.client.table("tasks").update(data).eq("id", task_id).execute()
        return result.data[0] if result.data else None

    async def delete(self, task_id: str) -> bool:
        if self.client is None:
            return False
        
        self.client.table("tasks").delete().eq("id", task_id).execute()
        return True