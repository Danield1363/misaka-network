from __future__ import annotations
import logging
from typing import Any
from app.services.supabase import get_supabase_client
from app.memory.errors import MemoryError

logger = logging.getLogger(__name__)


class MemoryRepository:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            raise MemoryError("Supabase not configured")
        
        result = self.client.table("memories").insert(data).execute()
        return result.data[0] if result.data else {}

    async def get(self, memory_id: str) -> dict[str, Any] | None:
        if self.client is None:
            return None
        
        result = self.client.table("memories").select("*").eq("id", memory_id).execute()
        return result.data[0] if result.data else None

    async def list(self, limit: int = 50) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        
        result = self.client.table("memories").select("*").order("created_at", desc=True).limit(limit).execute()
        return result.data or []

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        
        result = self.client.table("memories").select("*").ilike("content", f"%{query}%").limit(limit).execute()
        return result.data or []

    async def delete(self, memory_id: str) -> bool:
        if self.client is None:
            return False
        
        self.client.table("memories").delete().eq("id", memory_id).execute()
        return True

    async def save_conversation(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            return {}
        
        result = self.client.table("conversations").insert(data).execute()
        return result.data[0] if result.data else {}