from typing import Any
from app.tools.base import ToolBase
from app.calendar.scheduler import SchedulerEngine


class RunSchedulerTool(ToolBase):
    name: str = "scheduler.run"
    description: str = "Run the scheduler to process due reminders"
    category: str = "scheduler"
    danger_level: str = "safe"

    def __init__(self) -> None:
        self.engine = SchedulerEngine()

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        result = await self.engine.run_due_reminders()
        return {"success": True, "data": result, "metadata": {}}