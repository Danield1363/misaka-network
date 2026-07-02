from __future__ import annotations
import logging
from typing import Any
from datetime import datetime, timezone
from app.services.supabase import get_supabase_client
from app.actions.errors import ActionError

logger = logging.getLogger(__name__)


class ActionRepository:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            return {"id": "local", **data}
        result = self.client.table("action_logs").insert(data).execute()
        return result.data[0] if result.data else {}

    async def update(self, action_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        if self.client is None:
            return None
        result = self.client.table("action_logs").update(data).eq("id", action_id).execute()
        return result.data[0] if result.data else None

    async def list(self, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        query = self.client.table("action_logs").select("*")
        if status:
            query = query.eq("status", status)
        result = query.order("created_at", desc=True).limit(limit).execute()
        return result.data or []

    async def get(self, action_id: str) -> dict[str, Any] | None:
        if self.client is None:
            return None
        result = self.client.table("action_logs").select("*").eq("id", action_id).execute()
        return result.data[0] if result.data else None