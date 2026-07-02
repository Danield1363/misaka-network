import logging
from typing import Any
from app.agents.base import BaseAgent
from app.llm.gateway import LLMGateway

logger = logging.getLogger(__name__)


class ConversationAgent(BaseAgent):
    name: str = "conversation"
    description: str = "Agent for general conversation"

    def __init__(self) -> None:
        self.llm_gateway = LLMGateway()

    async def run(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"ConversationAgent processing: {message[:50]}...")
        
        try:
            llm_result = await self.llm_gateway.generate(message, context)
            
            return {
                "response": llm_result["response"],
                "agent": self.name,
                "model": llm_result.get("model"),
                "metadata": {
                    "provider": llm_result["provider"],
                    "mock": llm_result["provider"] == "mock"
                }
            }
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return {
                "response": f"Desculpe, ocorreu um erro ao processar sua mensagem.",
                "agent": self.name,
                "model": None,
                "metadata": {
                    "error": str(e),
                    "mock": True
                }
            }