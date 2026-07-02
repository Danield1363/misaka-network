from typing import Any
from app.tools.base import ToolBase
from app.tools.errors import ToolNotFoundError


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolBase] = {}

    def register(self, tool: ToolBase) -> None:
        if tool.name in self._tools:
            return
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolBase:
        tool = self._tools.get(name)
        if tool is None:
            raise ToolNotFoundError(f"Tool '{name}' not found")
        return tool

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "danger_level": t.danger_level,
                "requires_confirmation": t.requires_confirmation
            }
            for t in self._tools.values()
        ]

    def has_tool(self, name: str) -> bool:
        return name in self._tools


registry = ToolRegistry()


def register_default_tools() -> None:
    from app.tools.memory.tools import CreateMemoryTool, SearchMemoryTool
    from app.tools.tasks.tools import CreateTaskTool, ListTasksTool, CompleteTaskTool
    from app.tools.calendar.tools import CreateEventTool, ListEventsTool
    from app.tools.reminders.tools import CreateReminderTool, ListRemindersTool
    from app.tools.scheduler.tools import RunSchedulerTool

    for tool_class in [
        CreateMemoryTool, SearchMemoryTool,
        CreateTaskTool, ListTasksTool, CompleteTaskTool,
        CreateEventTool, ListEventsTool,
        CreateReminderTool, ListRemindersTool,
        RunSchedulerTool
    ]:
        registry.register(tool_class())


register_default_tools()