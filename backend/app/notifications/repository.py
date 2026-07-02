from __future__ import annotations
import logging
from typing import Any
from datetime import datetime, timezone
from app.services.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class NotificationRepository:
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
        result = self.client.table("notifications").insert(data).execute()
        return result.data[0] if result.data else {}

    async def list(self, importance: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        query = self.client.table("notifications").select("*")
        if importance:
            query = query.eq("importance", importance)
        result = query.order("received_at", desc=True).limit(limit).execute()
        return result.data or []

    async def create_alert(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            return {"id": "local", **data}
        result = self.client.table("important_alerts").insert(data).execute()
        return result.data[0] if result.data else {}

    async def list_alerts(self, status: str | None = None) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        query = self.client.table("important_alerts").select("*")
        if status:
            query = query.eq("status", status)
        result = query.order("created_at", desc=True).execute()
        return result.data or []

    async def acknowledge_alert(self, alert_id: str) -> dict[str, Any] | None:
        if self.client is None:
            return None
        data = {"status": "acknowledged", "acknowledged_at": datetime.now(timezone.utc).isoformat()}
        result = self.client.table("important_alerts").update(data).eq("id", alert_id).execute()
        return result.data[0] if result.data else None