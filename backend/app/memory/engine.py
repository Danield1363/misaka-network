import logging
from typing import Any
from app.memory.repository import MemoryRepository
from app.services.supabase import is_memory_enabled

logger = logging.getLogger(__name__)


class MemoryEngine:
    def __init__(self) -> None:
        self.repository = MemoryRepository()
        self.enabled = is_memory_enabled()

    async def create_memory(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {}
        
        try:
            return await self.repository.create(data)
        except Exception as e:
            logger.error(f"Failed to create memory: {e}")
            return {}

    async def search_memories(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        
        try:
            return await self.repository.search(query, limit)
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []

    async def get_relevant_context(self, message: str) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        
        try:
            return await self.repository.search(message, limit=5)
        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            return []

    async def save_interaction(
        self,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        metadata: dict[str, Any]
    ) -> dict[str, Any]:
        if not self.enabled:
            return {}
        
        try:
            data = {
                "conversation_id": conversation_id,
                "user_message": user_message,
                "assistant_response": assistant_response,
                "metadata": metadata
            }
            return await self.repository.save_conversation(data)
        except Exception as e:
            logger.error(f"Failed to save interaction: {e}")
            return {}