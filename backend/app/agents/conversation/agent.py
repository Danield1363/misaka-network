import logging
from typing import Any
from app.agents.base import BaseAgent
from app.llm.gateway import LLMGateway
from app.persona.engine import PersonaEngine

logger = logging.getLogger(__name__)


class ConversationAgent(BaseAgent):
    name: str = "conversation"
    description: str = "Agent for general conversation"

    def __init__(self) -> None:
        self.llm_gateway = LLMGateway()
        self.persona_engine = PersonaEngine()

    async def run(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"ConversationAgent processing: {message[:50]}...")

        memories = context.get("memories", [])
        memory_context = ""
        if memories:
            memory_text = "\n".join([f"- {m.get('content', '')}" for m in memories[:5]])
            memory_context = f"\n\nMemórias relevantes:\n{memory_text}"

        system_prompt = self.persona_engine.get_system_prompt()

        enriched_context = {
            **context,
            "personality": f"{system_prompt}{memory_context}"
        }

        try:
            llm_result = await self.llm_gateway.generate(message, enriched_context)

            return {
                "response": llm_result["response"],
                "agent": self.name,
                "model": llm_result.get("model"),
                "metadata": {
                    "provider": llm_result["provider"],
                    "mock": llm_result["provider"] == "mock",
                    "memories_used": len(memories),
                    "llm_error": False
                }
            }
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return {
                "response": "Desculpe, ocorreu um erro ao processar sua mensagem. Verifique se o provedor LLM está configurado corretamente.",
                "agent": self.name,
                "model": None,
                "metadata": {
                    "error": str(e),
                    "mock": True,
                    "llm_error": True,
                    "provider": self.llm_gateway.default_provider
                }
            }