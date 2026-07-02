from typing import Any


class ToolBase:
    name: str = "base"
    description: str = "Base tool"
    category: str = "general"
    requires_confirmation: bool = False
    danger_level: str = "safe"

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError("Subclasses must implement run method")