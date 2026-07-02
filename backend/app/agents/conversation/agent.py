import logging
from typing import Any
from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class ConversationAgent(BaseAgent):
    name: str = "conversation"
    description: str = "Agent for general conversation"

    async def run(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"ConversationAgent processing: {message[:50]}...")
        
        lower_message = message.lower().strip()
        greetings = ["olá", "ola", "hi", "hello", "ei", "hey"]
        
        is_greeting = any(lower_message.startswith(g) or lower_message == g for g in greetings)
        
        if is_greeting:
            response = "Olá, eu sou a Misaka. Meu Brain Engine já está online."
        else:
            response = f"Recebi sua mensagem: {message}"
        
        return {
            "response": response,
            "agent": self.name,
            "model": None,
            "metadata": {
                "mock": True
            }
        }