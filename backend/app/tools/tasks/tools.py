from typing import Any
from app.tools.base import ToolBase
from app.tasks.engine import TaskEngine


class CreateTaskTool(ToolBase):
    name: str = "tasks.create"
    description: str = "Create a new task"
    category: str = "tasks"
    danger_level: str = "low"

    def __init__(self) -> None:
        self.engine = TaskEngine()

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        result = await self.engine.create_task(input_data)
        return {"success": bool(result), "data": result, "metadata": {}}


class ListTasksTool(ToolBase):
    name: str = "tasks.list"
    description: str = "List tasks"
    category: str = "tasks"
    danger_level: str = "safe"

    def __init__(self) -> None:
        self.engine = TaskEngine()

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        status = input_data.get("status")
        results = await self.engine.list_tasks(status)
        return {"success": True, "data": {"tasks": results, "total": len(results)}, "metadata": {}}


class CompleteTaskTool(ToolBase):
    name: str = "tasks.complete"
    description: str = "Mark a task as completed"
    category: str = "tasks"
    danger_level: str = "low"

    def __init__(self) -> None:
        self.engine = TaskEngine()

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        task_id = input_data.get("task_id", "")
        result = await self.engine.complete_task(task_id)
        return {"success": bool(result), "data": result, "metadata": {}}