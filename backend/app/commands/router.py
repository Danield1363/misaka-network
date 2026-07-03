import logging
import re
from typing import Any
from app.commands.parser import (
    detect_intent,
    extract_url,
    extract_task_description,
    extract_reminder_text,
    extract_memory_content,
    extract_app_name,
    extract_search_query,
)
from app.commands.intents import Intent
from app.commands.desktop_resolver import detect_desktop_command, normalize_text
from app.tools.executor import ToolExecutor
from app.web_actions.engine import WebActionEngine

logger = logging.getLogger(__name__)

web_action_engine = WebActionEngine()

DANGEROUS_COMMAND_PATTERNS = [
    r"\bdeslig(?:ar|ue|a)\s+(?:o\s+)?(?:computador|pc)\b",
    r"\breinici(?:ar|e|a)\s+(?:o\s+)?(?:computador|pc)\b",
    r"\b(?:apagar|deletar|remover)\s+(?:arquivo|pasta|diretorio)\b",
    r"\bformatar\b",
    r"\brodar\s+script\b",
    r"\bexecutar\s+terminal\b",
    r"\benviar\s+mensagem\b",
    r"\bcomprar\b",
    r"\bpagar\b",
]


class CommandRouter:
    def __init__(self) -> None:
        self.executor = ToolExecutor()

    async def route(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        dangerous_result = self._route_dangerous_command(message)
        if dangerous_result is not None:
            return dangerous_result

        desktop_cmd = detect_desktop_command(message)
        if desktop_cmd.matched:
            logger.info(
                "[CommandRouter] matched open_app %s (confidence=%.2f)",
                desktop_cmd.app,
                desktop_cmd.confidence,
            )
            return {
                "type": "command_executed",
                "intent": desktop_cmd.intent,
                "command": desktop_cmd.command,
                "tool_name": "desktop.open_app",
                "success": True,
                "data": {"app": desktop_cmd.app},
                "response_message": desktop_cmd.response_message,
                "client_action": {
                    "type": "open_app",
                    "target": desktop_cmd.target_device,
                    "app": desktop_cmd.app,
                },
                "metadata": {
                    "response_mode": "action_short",
                    "ui_effect": "none",
                },
            }

        web_result = web_action_engine.process(message)
        if web_result:
            client_action = self._build_web_client_action(web_result)
            web_command = (
                "search_web"
                if client_action.get("type") == "search_web"
                else "open_url"
            )
            logger.info(
                "[CommandRouter] matched %s -> %s",
                web_result.action_type,
                web_result.url,
            )
            return {
                "type": "command_executed",
                "intent": "web_action",
                "command": web_command,
                "tool_name": "desktop.open_url",
                "success": True,
                "data": {"url": web_result.url},
                "response_message": web_result.response_message,
                "client_action": client_action,
                "metadata": {
                    "response_mode": "action_short",
                    "ui_effect": "none",
                },
            }

        intent = detect_intent(message)

        if intent is None:
            logger.info("[CommandRouter] no command matched for: %s", message[:80])
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

        client_action = self._build_client_action(intent.name, input_data, message)

        try:
            result = await self.executor.execute(
                tool_name=intent.tool_name,
                input_data=input_data,
                context=context or {},
            )
            response = {
                "type": "command_executed",
                "intent": intent.name,
                "tool_name": intent.tool_name,
                "success": result.get("success", False),
                "data": result.get("data", {}),
                "response_message": intent.response_message,
                "metadata": result.get("metadata", {}),
            }
            if client_action:
                response["client_action"] = client_action
            return response
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                "type": "command_error",
                "intent": intent.name,
                "tool_name": intent.tool_name,
                "error": str(e),
                "response_message": f"Erro ao executar comando: {e}",
            }

    def _route_dangerous_command(self, message: str) -> dict[str, Any] | None:
        normalized = normalize_text(message)
        if not any(re.search(pattern, normalized) for pattern in DANGEROUS_COMMAND_PATTERNS):
            return None

        from app.commands.confirmations import confirmation_manager

        conf = confirmation_manager.create_confirmation(
            intent="dangerous_desktop_action",
            tool_name="desktop.confirmed_action",
            parameters={"text": message},
            message=(
                "Esse comando pode afetar o computador e requer confirmacao. "
                "Posso continuar?"
            ),
            original_message=message,
        )
        return {
            "type": "confirmation_required",
            "intent": "dangerous_desktop_action",
            "tool_name": "desktop.confirmed_action",
            "message": conf.message,
            "confirmation_id": conf.id,
            "parameters": {"text": message},
        }

    def _build_client_action(
        self, intent_name: str, parameters: dict, message: str
    ) -> dict[str, Any] | None:
        if intent_name in ("open_youtube", "open_url_site"):
            url = (
                parameters.get("url")
                or extract_url(message)
                or "https://www.youtube.com"
            )
            return {"type": "open_url", "target": "desktop", "url": url}

        if intent_name == "open_app":
            app = extract_app_name(message)
            return {"type": "open_app", "target": "desktop", "app": app}

        if intent_name == "open_browser":
            return {"type": "open_app", "target": "desktop", "app": "browser"}

        if intent_name == "search_web":
            query = extract_search_query(message)
            return {
                "type": "search_web",
                "target": "desktop",
                "provider": "google",
                "query": query,
            }

        if intent_name == "pc_status":
            return {"type": "get_system_status", "target": "desktop"}

        if intent_name == "android_vibrate":
            return {"type": "vibrate", "target": "android"}

        if intent_name == "android_toast":
            return {
                "type": "show_toast",
                "target": "android",
                "message": "Alerta do Misaka",
            }

        return None

    def _build_web_client_action(self, web_result: Any) -> dict[str, Any]:
        if web_result.action_type in {
            "search_google",
            "open_youtube_search",
            "search_github",
            "search_reddit",
            "search_wikipedia",
            "search_site",
            "search_web",
        }:
            provider_map = {
                "search_google": "google",
                "open_youtube_search": "youtube",
                "search_github": "github",
                "search_reddit": "reddit",
                "search_wikipedia": "google",
                "search_site": web_result.site or "google",
                "search_web": "google",
            }
            return {
                "type": "search_web",
                "target": web_result.target,
                "provider": provider_map.get(web_result.action_type, "google"),
                "query": web_result.query,
                "url": web_result.url,
                "source": "web_action_engine",
            }

        return {
            "type": "open_url",
            "target": web_result.target,
            "url": web_result.url,
            "source": "web_action_engine",
        }
