from typing import Any


class BaseAgent:
    name: str = "base"
    description: str = "Base agent"

    async def run(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Subclasses must implement run method")