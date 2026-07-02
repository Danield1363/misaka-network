import logging
from typing import Any
from app.calendar.repository import CalendarRepository
from app.services.supabase import is_memory_enabled

logger = logging.getLogger(__name__)


class ReminderEngine:
    def __init__(self) -> None:
        self.repository = CalendarRepository()
        self.enabled = is_memory_enabled()

    async def create_reminder(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {}
        try:
            data["status"] = "pending"
            data["source"] = "misaka"
            return await self.repository.create_reminder(data)
        except Exception as e:
            logger.error(f"Failed to create reminder: {e}")
            return {}

    async def list_reminders(self, status: str | None = None) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            return await self.repository.list_reminders(status)
        except Exception as e:
            logger.error(f"Failed to list reminders: {e}")
            return []

    async def complete_reminder(self, reminder_id: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        try:
            return await self.repository.update_reminder(reminder_id, {"status": "done"})
        except Exception as e:
            logger.error(f"Failed to complete reminder: {e}")
            return None

    async def cancel_reminder(self, reminder_id: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        try:
            return await self.repository.update_reminder(reminder_id, {"status": "cancelled"})
        except Exception as e:
            logger.error(f"Failed to cancel reminder: {e}")
            return None

    async def get_pending_reminders(self) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            return await self.repository.list_reminders("pending")
        except Exception as e:
            logger.error(f"Failed to get pending reminders: {e}")
            return []

    async def update_reminder(self, reminder_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        try:
            return await self.repository.update_reminder(reminder_id, data)
        except Exception as e:
            logger.error(f"Failed to update reminder: {e}")
            return None

    async def delete_reminder(self, reminder_id: str) -> bool:
        if not self.enabled:
            return False
        try:
            return await self.repository.delete_reminder(reminder_id)
        except Exception as e:
            logger.error(f"Failed to delete reminder: {e}")
            return False