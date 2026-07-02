from typing import Protocol, Any


class AgentProtocol(Protocol):
    name: str
    description: str

    async def run(self, message: str, context: dict[str, Any]) -> dict[str, Any]: ...


class PlannerProtocol(Protocol):
    def detect_intent(self, message: str) -> str: ...


class OrchestratorProtocol(Protocol):
    async def execute(self, intent: str, message: str, context: dict[str, Any]) -> dict[str, Any]: ...