import logging
from typing import Any
from datetime import datetime, timezone
from app.calendar.repository import CalendarRepository
from app.services.supabase import is_memory_enabled

logger = logging.getLogger(__name__)


class CalendarEngine:
    def __init__(self) -> None:
        self.repository = CalendarRepository()
        self.enabled = is_memory_enabled()

    async def create_event(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {}
        try:
            data["status"] = "scheduled"
            data["source"] = "misaka"
            return await self.repository.create_event(data)
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return {}

    async def list_events(self, from_date: str | None = None, to_date: str | None = None) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            return await self.repository.list_events(from_date, to_date)
        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            return []

    async def update_event(self, event_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        try:
            return await self.repository.update_event(event_id, data)
        except Exception as e:
            logger.error(f"Failed to update event: {e}")
            return None

    async def cancel_event(self, event_id: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        try:
            return await self.repository.update_event(event_id, {"status": "cancelled"})
        except Exception as e:
            logger.error(f"Failed to cancel event: {e}")
            return None

    async def get_today_events(self) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            now = datetime.now(timezone.utc)
            start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
            return await self.repository.list_events(start, end)
        except Exception as e:
            logger.error(f"Failed to get today events: {e}")
            return []

    async def get_upcoming_events(self, days: int = 7) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            now = datetime.now(timezone.utc)
            start = now.isoformat()
            from datetime import timedelta
            end = (now + timedelta(days=days)).isoformat()
            return await self.repository.list_events(start, end)
        except Exception as e:
            logger.error(f"Failed to get upcoming events: {e}")
            return []