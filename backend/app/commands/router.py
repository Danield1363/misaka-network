import logging
from typing import Any
from app.commands.parser import (
    detect_intent,
    extract_task_description,
    extract_reminder_text,
    extract_memory_content,
    extract_app_name,
    extract_search_query,
)
from app.commands.intents import Intent
from app.tools.executor import ToolExecutor

logger = logging.getLogger(__name__)


class CommandRouter:
    def __init__(self) -> None:
        self.executor = ToolExecutor()

    async def route(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        intent = detect_intent(message)

        if intent is None:
            return None

        logger.info(
            f"Command detected: {intent.name} (confidence: {intent.confidence})"
        )

        if intent.requires_confirmation:
            from app.commands.confirmations import confirmation_manager

            conf = confirmation_manager.create_confirmation(
                intent=intent.name,
                tool_name=intent.tool_name or "",
                parameters=dict(intent.parameters),
                message=(
                    intent.response_message
                    or f"A ação '{intent.name}' requer confirmação. Posso executar?"
                ),
                original_message=message,
            )
            return {
                "type": "confirmation_required",
                "intent": intent.name,
                "tool_name": intent.tool_name,
                "message": conf.message,
                "confirmation_id": conf.id,
                "parameters": intent.parameters,
            }

        input_data = dict(intent.parameters)

        if intent.tool_name == "tasks.create":
            input_data["title"] = extract_task_description(message)
        elif intent.tool_name == "reminders.create":
            input_data["text"] = extract_reminder_text(message)
        elif intent.tool_name == "memory.create":
            input_data["content"] = extract_memory_content(message)
        elif intent.tool_name == "desktop.open_app":
            input_data["app"] = extract_app_name(message)
        elif intent.tool_name == "desktop.search_web":
            input_data["query"] = extract_search_query(message)

        try:
            result = await self.executor.execute(
                tool_name=intent.tool_name,
                input_data=input_data,
                context=context or {},
            )
            return {
                "type": "command_executed",
                "intent": intent.name,
                "tool_name": intent.tool_name,
                "success": result.get("success", False),
                "data": result.get("data", {}),
                "response_message": intent.response_message,
                "metadata": result.get("metadata", {}),
            }
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                "type": "command_error",
                "intent": intent.name,
                "tool_name": intent.tool_name,
                "error": str(e),
                "response_message": f"Erro ao executar comando: {e}",
            }
