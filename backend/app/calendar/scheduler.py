import logging
from typing import Any
from datetime import datetime, timezone
from app.calendar.repository import CalendarRepository
from app.services.supabase import is_memory_enabled

logger = logging.getLogger(__name__)


class SchedulerEngine:
    def __init__(self) -> None:
        self.repository = CalendarRepository()
        self.enabled = is_memory_enabled()

    async def run_due_reminders(self) -> dict[str, Any]:
        if not self.enabled:
            return {"processed_reminders": 0, "created_notifications": 0, "status": "disabled"}

        try:
            due_reminders = await self.repository.get_due_reminders()
            processed = 0
            created = 0

            for reminder in due_reminders:
                notification_data = {
                    "type": "reminder",
                    "title": reminder.get("title", ""),
                    "message": reminder.get("description", reminder.get("title", "")),
                    "status": "pending",
                    "target": "default",
                    "payload": {"reminder_id": reminder.get("id")},
                    "scheduled_for": reminder.get("remind_at")
                }

                notification = await self.repository.create_notification(notification_data)
                if notification:
                    created += 1

                await self.repository.mark_reminder_triggered(reminder.get("id"))
                processed += 1

            return {
                "processed_reminders": processed,
                "created_notifications": created,
                "status": "ok"
            }
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            return {"processed_reminders": 0, "created_notifications": 0, "status": "error"}