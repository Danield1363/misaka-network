import uuid
import time
import logging
from typing import Any
from app.schemas.chat import ChatResponse
from app.brain.planner import Planner
from app.brain.orchestrator import Orchestrator
from app.brain.personality import PersonalityEngine
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class BrainEngine:
    def __init__(self) -> None:
        self.planner = Planner()
        self.orchestrator = Orchestrator()
        self.personality = PersonalityEngine()
        self.settings = get_settings()

    async def process_message(
        self,
        message: str,
        conversation_id: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> ChatResponse:
        start_time = time.time()
        
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        logger.info(f"Processing message in conversation {conversation_id}")
        
        intent = self.planner.detect_intent(message)
        logger.info(f"Detected intent: {intent}")
        
        context = {
            "conversation_id": conversation_id,
            "personality": self.personality.get_prompt(),
            "metadata": metadata or {}
        }
        
        agent_result = await self.orchestrator.execute(intent, message, context)
        
        execution_time = time.time() - start_time
        
        response_metadata = {
            "intent": intent,
            "version": self.settings.VERSION,
            **agent_result.get("metadata", {})
        }
        
        return ChatResponse(
            response=agent_result["response"],
            agent=agent_result["agent"],
            model=agent_result.get("model"),
            execution_time=round(execution_time, 4),
            conversation_id=conversation_id,
            metadata=response_metadata
        )