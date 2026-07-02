from typing import Protocol, Any


class LLMProviderProtocol(Protocol):
    name: str

    async def generate(self, message: str, context: dict[str, Any]) -> str: ...

    def is_available(self) -> bool: ...