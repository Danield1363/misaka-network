from typing import Any
from app.tools.base import ToolBase
from app.calendar.reminder_engine import ReminderEngine


class CreateReminderTool(ToolBase):
    name: str = "reminders.create"
    description: str = "Create a reminder"
    category: str = "reminders"
    danger_level: str = "low"

    def __init__(self) -> None:
        self.engine = ReminderEngine()

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        result = await self.engine.create_reminder(input_data)
        return {"success": bool(result), "data": result, "metadata": {}}


class ListRemindersTool(ToolBase):
    name: str = "reminders.list"
    description: str = "List reminders"
    category: str = "reminders"
    danger_level: str = "safe"

    def __init__(self) -> None:
        self.engine = ReminderEngine()

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        status = input_data.get("status")
        results = await self.engine.list_reminders(status)
        return {"success": True, "data": {"reminders": results, "total": len(results)}, "metadata": {}}