from __future__ import annotations
import logging
from typing import Any
from datetime import datetime, timezone
from app.services.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class AndroidRepository:
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
        result = self.client.table("android_actions").insert(data).execute()
        return result.data[0] if result.data else {}

    async def list_pending(self, device_id: str | None = None) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        query = self.client.table("android_actions").select("*").eq("status", "pending")
        if device_id:
            query = query.eq("device_id", device_id)
        result = query.order("created_at", desc=False).limit(50).execute()
        return result.data or []

    async def complete(self, action_id: str, result_data: dict[str, Any] | None = None) -> bool:
        if self.client is None:
            return False
        data = {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        if result_data:
            data["result"] = result_data
        self.client.table("android_actions").update(data).eq("id", action_id).execute()
        return True

    async def fail(self, action_id: str, error_message: str = "") -> bool:
        if self.client is None:
            return False
        data = {
            "status": "failed",
            "error_message": error_message,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("android_actions").update(data).eq("id", action_id).execute()
        return True

    async def cancel(self, action_id: str) -> bool:
        if self.client is None:
            return False
        data = {"status": "cancelled", "completed_at": datetime.now(timezone.utc).isoformat()}
        self.client.table("android_actions").update(data).eq("id", action_id).execute()
        return True
