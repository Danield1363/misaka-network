from typing import Any
from app.tools.base import ToolBase
from app.calendar.engine import CalendarEngine


class CreateEventTool(ToolBase):
    name: str = "calendar.create_event"
    description: str = "Create a calendar event"
    category: str = "calendar"
    danger_level: str = "low"

    def __init__(self) -> None:
        self.engine = CalendarEngine()

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        result = await self.engine.create_event(input_data)
        return {"success": bool(result), "data": result, "metadata": {}}


class ListEventsTool(ToolBase):
    name: str = "calendar.list_events"
    description: str = "List calendar events"
    category: str = "calendar"
    danger_level: str = "safe"

    def __init__(self) -> None:
        self.engine = CalendarEngine()

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from_date = input_data.get("from_date")
        to_date = input_data.get("to_date")
        results = await self.engine.list_events(from_date, to_date)
        return {"success": True, "data": {"events": results, "total": len(results)}, "metadata": {}}