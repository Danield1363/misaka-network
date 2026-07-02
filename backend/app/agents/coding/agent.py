import logging
from typing import Any
from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class CodingAgent(BaseAgent):
    name: str = "coding"
    description: str = "Agent for coding tasks (mock)"

    async def run(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"CodingAgent processing: {message[:50]}...")
        return {
            "response": "Entendi que essa é uma tarefa de programação. Por enquanto, o Coding Agent está em modo mock.",
            "agent": self.name,
            "model": None,
            "metadata": {
                "mock": True,
                "agent_type": "coding"
            }
        }