import uuid
import time
import logging
from typing import Any
from app.schemas.chat import ChatResponse
from app.brain.planner import Planner
from app.brain.orchestrator import Orchestrator
from app.brain.personality import PersonalityEngine
from app.memory.engine import MemoryEngine
from app.persona.engine import PersonaEngine
from app.core.config import get_settings

logger = logging.getLogger(__name__)

UI_EFFECT_MAP = {
    "clear_alerts": "refresh_alerts",
    "show_alerts": "refresh_alerts",
    "hud_on": "enable_hud",
    "hud_off": "disable_hud",
    "open_settings": "open_settings",
    "clear_chat": "clear_chat",
    "voice_on": "enable_voice",
    "voice_off": "disable_voice",
    "voice_female": "enable_voice",
    "open_browser": "none",
    "open_app": "none",
    "open_url": "none",
    "search_web": "none",
    "pc_status": "refresh_status",
    "android_vibrate": "none",
    "android_open_app": "none",
    "android_toast": "none",
    "android_status": "refresh_status",
    "create_task": "none",
    "list_tasks": "none",
    "complete_task": "none",
    "remember": "none",
    "recall": "none",
    "forget": "none",
    "create_reminder": "none",
    "list_reminders": "none",
}


class BrainEngine:
    def __init__(self) -> None:
        self.planner = Planner()
        self.orchestrator = Orchestrator()
        self.personality = PersonalityEngine()
        self.memory_engine = MemoryEngine()
        self.persona_engine = PersonaEngine()
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

        memories = await self.memory_engine.get_relevant_context(message)
        memory_enabled = self.memory_engine.enabled

        from app.commands.router import CommandRouter
        router = CommandRouter()
        result = await router.route(message)
        if result is not None:
            if result.get("type") == "command_executed":
                response_text = result.get("response_message", "Comando executado.")
                formatted_response = self.persona_engine.format_response(response_text)

                await self.memory_engine.save_interaction(
                    conversation_id=conversation_id,
                    user_message=message,
                    assistant_response=formatted_response,
                    metadata={"intent": "command", "command": result.get("intent")},
                )

                command_intent = result.get("intent", "")
                command_name = result.get("command") or command_intent
                if command_intent in ("desktop", "web_action"):
                    metadata_intent = command_intent
                else:
                    metadata_intent = "command"
                    command_name = command_intent
                response_metadata = {
                    "intent": metadata_intent,
                    "command": command_name,
                    "tool_name": result.get("tool_name"),
                    "action_taken": result.get("tool_name"),
                    "ui_effect": UI_EFFECT_MAP.get(
                        command_name, UI_EFFECT_MAP.get(command_intent, "")
                    ),
                    "version": self.settings.VERSION,
                    "memory_enabled": memory_enabled,
                    "memories_used": len(memories),
                    **result.get("metadata", {}),
                }
                if result.get("client_action"):
                    response_metadata["client_action"] = result["client_action"]

                return ChatResponse(
                    response=formatted_response,
                    agent="command_router",
                    model=None,
                    execution_time=round(time.time() - start_time, 4),
                    conversation_id=conversation_id,
                    metadata=response_metadata,
                )

            if result.get("type") == "confirmation_required":
                response_text = result.get("message", "Essa acao requer confirmacao.")
                formatted_response = self.persona_engine.format_response(response_text)

                return ChatResponse(
                    response=formatted_response,
                    agent="command_router",
                    model=None,
                    execution_time=round(time.time() - start_time, 4),
                    conversation_id=conversation_id,
                    metadata={
                        "intent": "command",
                        "command": result.get("intent"),
                        "requires_confirmation": True,
                        "confirmation_id": result.get("confirmation_id"),
                        "version": self.settings.VERSION,
                        "memory_enabled": memory_enabled,
                        "memories_used": len(memories),
                    },
                )

        logger.info("[CommandRouter] no command matched, falling back to LLM for: %s", message[:80])
        intent = self.planner.detect_intent(message)
        logger.info(f"Detected intent: {intent}")

        if intent == "command":
            from app.commands.router import CommandRouter
            router = CommandRouter()
            result = await router.route(message)

            if result is None:
                logger.warning("CommandRouter returned None for command intent")
            elif result.get("type") == "command_executed":
                response_text = result.get("response_message", "Comando executado.")
                formatted_response = self.persona_engine.format_response(response_text)

                await self.memory_engine.save_interaction(
                    conversation_id=conversation_id,
                    user_message=message,
                    assistant_response=formatted_response,
                    metadata={"intent": "command", "command": result.get("intent")},
                )

                execution_time = time.time() - start_time
                command_intent = result.get("intent", "")
                command_name = result.get("command") or command_intent
                if command_intent in ("desktop", "web_action"):
                    metadata_intent = command_intent
                else:
                    metadata_intent = "command"
                    command_name = command_intent
                response_metadata = {
                    "intent": metadata_intent,
                    "command": command_name,
                    "tool_name": result.get("tool_name"),
                    "action_taken": result.get("tool_name"),
                    "ui_effect": UI_EFFECT_MAP.get(
                        command_name, UI_EFFECT_MAP.get(command_intent, "")
                    ),
                    "version": self.settings.VERSION,
                    "memory_enabled": memory_enabled,
                    "memories_used": len(memories),
                    **result.get("metadata", {}),
                }
                if result.get("client_action"):
                    response_metadata["client_action"] = result["client_action"]

                return ChatResponse(
                    response=formatted_response,
                    agent="command_router",
                    model=None,
                    execution_time=round(execution_time, 4),
                    conversation_id=conversation_id,
                    metadata=response_metadata,
                )
            elif result.get("type") == "confirmation_required":
                response_text = result.get("message", "Essa ação requer confirmação.")
                formatted_response = self.persona_engine.format_response(response_text)

                execution_time = time.time() - start_time
                return ChatResponse(
                    response=formatted_response,
                    agent="command_router",
                    model=None,
                    execution_time=round(execution_time, 4),
                    conversation_id=conversation_id,
                    metadata={
                        "intent": "command",
                        "command": result.get("intent"),
                        "requires_confirmation": True,
                        "confirmation_id": result.get("confirmation_id"),
                        "version": self.settings.VERSION,
                        "memory_enabled": memory_enabled,
                    },
                )

        context = {
            "conversation_id": conversation_id,
            "personality": self.personality.get_prompt(),
            "metadata": metadata or {},
            "memories": memories,
        }

        agent_result = await self.orchestrator.execute(intent, message, context)

        formatted_response = self.persona_engine.format_response(agent_result["response"])

        await self.memory_engine.save_interaction(
            conversation_id=conversation_id,
            user_message=message,
            assistant_response=formatted_response,
            metadata={"intent": intent},
        )

        execution_time = time.time() - start_time

        response_metadata = {
            "intent": intent,
            "version": self.settings.VERSION,
            "memory_enabled": memory_enabled,
            "memories_used": len(memories),
            **agent_result.get("metadata", {}),
        }

        return ChatResponse(
            response=formatted_response,
            agent=agent_result["agent"],
            model=agent_result.get("model"),
            execution_time=round(execution_time, 4),
            conversation_id=conversation_id,
            metadata=response_metadata,
        )
