import logging
from typing import Any

logger = logging.getLogger(__name__)


class MockProvider:
    name: str = "mock"

    async def generate(self, message: str, context: dict[str, Any]) -> str:
        logger.info(f"MockProvider generating response for: {message[:50]}...")
        
        lower_message = message.lower().strip()
        greetings = ["olá", "ola", "hi", "hello", "ei", "hey"]
        
        is_greeting = any(lower_message.startswith(g) or lower_message == g for g in greetings)
        
        if is_greeting:
            return "Olá, eu sou a Misaka. Meu Brain Engine já está online."
        
        return f"Recebi sua mensagem: {message}"

    def is_available(self) -> bool:
        return True