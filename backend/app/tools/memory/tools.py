from typing import Any
from app.tools.base import ToolBase
from app.memory.engine import MemoryEngine


class CreateMemoryTool(ToolBase):
    name: str = "memory.create"
    description: str = "Create a new memory"
    category: str = "memory"
    danger_level: str = "low"

    def __init__(self) -> None:
        self.engine = MemoryEngine()

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        result = await self.engine.create_memory(input_data)
        return {"success": bool(result), "data": result, "metadata": {}}


class SearchMemoryTool(ToolBase):
    name: str = "memory.search"
    description: str = "Search memories by query"
    category: str = "memory"
    danger_level: str = "safe"

    def __init__(self) -> None:
        self.engine = MemoryEngine()

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        query = input_data.get("query", "")
        results = await self.engine.search_memories(query)
        return {"success": True, "data": {"results": results, "total": len(results)}, "metadata": {}}