import logging
from typing import Any
from app.agents.conversation.agent import ConversationAgent

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self) -> None:
        self.agents: dict[str, Any] = {
            "conversation": ConversationAgent()
        }

    async def execute(self, intent: str, message: str, context: dict[str, Any]) -> dict[str, Any]:
        agent = self.agents.get(intent)
        
        if agent is None:
            logger.warning(f"Agent not found for intent: {intent}, using conversation agent")
            agent = self.agents["conversation"]
        
        logger.info(f"Executing agent: {agent.name}")
        return await agent.run(message, context)