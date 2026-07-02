from __future__ import annotations
import logging
from typing import Any
from datetime import datetime, timezone
from app.services.supabase import get_supabase_client
from app.calendar.errors import CalendarError

logger = logging.getLogger(__name__)


class CalendarRepository:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def create_event(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            raise CalendarError("Supabase not configured")
        result = self.client.table("calendar_events").insert(data).execute()
        return result.data[0] if result.data else {}

    async def get_event(self, event_id: str) -> dict[str, Any] | None:
        if self.client is None:
            return None
        result = self.client.table("calendar_events").select("*").eq("id", event_id).execute()
        return result.data[0] if result.data else None

    async def list_events(self, from_date: str | None = None, to_date: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        query = self.client.table("calendar_events").select("*")
        if from_date:
            query = query.gte("starts_at", from_date)
        if to_date:
            query = query.lte("starts_at", to_date)
        result = query.order("starts_at", desc=False).limit(limit).execute()
        return result.data or []

    async def update_event(self, event_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        if self.client is None:
            return None
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = self.client.table("calendar_events").update(data).eq("id", event_id).execute()
        return result.data[0] if result.data else None

    async def delete_event(self, event_id: str) -> bool:
        if self.client is None:
            return False
        self.client.table("calendar_events").delete().eq("id", event_id).execute()
        return True

    async def create_reminder(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            raise CalendarError("Supabase not configured")
        result = self.client.table("reminders").insert(data).execute()
        return result.data[0] if result.data else {}

    async def get_reminder(self, reminder_id: str) -> dict[str, Any] | None:
        if self.client is None:
            return None
        result = self.client.table("reminders").select("*").eq("id", reminder_id).execute()
        return result.data[0] if result.data else None

    async def list_reminders(self, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        query = self.client.table("reminders").select("*")
        if status:
            query = query.eq("status", status)
        result = query.order("remind_at", desc=False).limit(limit).execute()
        return result.data or []

    async def update_reminder(self, reminder_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        if self.client is None:
            return None
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = self.client.table("reminders").update(data).eq("id", reminder_id).execute()
        return result.data[0] if result.data else None

    async def delete_reminder(self, reminder_id: str) -> bool:
        if self.client is None:
            return False
        self.client.table("reminders").delete().eq("id", reminder_id).execute()
        return True

    async def get_due_reminders(self) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        now = datetime.now(timezone.utc).isoformat()
        result = self.client.table("reminders").select("*").eq("status", "pending").lte("remind_at", now).execute()
        return result.data or []

    async def mark_reminder_triggered(self, reminder_id: str) -> dict[str, Any] | None:
        if self.client is None:
            return None
        data = {"status": "triggered", "updated_at": datetime.now(timezone.utc).isoformat()}
        result = self.client.table("reminders").update(data).eq("id", reminder_id).execute()
        return result.data[0] if result.data else None

    async def create_notification(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            return {}
        result = self.client.table("notification_outbox").insert(data).execute()
        return result.data[0] if result.data else {}

    async def list_notifications(self, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        query = self.client.table("notification_outbox").select("*")
        if status:
            query = query.eq("status", status)
        result = query.order("created_at", desc=True).limit(limit).execute()
        return result.data or []

    async def mark_notification_sent(self, notification_id: str) -> dict[str, Any] | None:
        if self.client is None:
            return None
        data = {"status": "sent", "sent_at": datetime.now(timezone.utc).isoformat()}
        result = self.client.table("notification_outbox").update(data).eq("id", notification_id).execute()
        return result.data[0] if result.data else None