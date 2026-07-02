from typing import Any
from app.tools.base import ToolBase


class SetHudModeTool(ToolBase):
    name = "ui.set_hud_mode"
    description = "Ativar ou desativar modo HUD"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        enabled = input_data.get("enabled", True)
        return {
            "data": {"hud_enabled": enabled},
            "metadata": {"action": "set_hud_mode", "enabled": enabled},
        }


class OpenSettingsTool(ToolBase):
    name = "ui.open_settings"
    description = "Abrir painel de configurações"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "data": {"settings_open": True},
            "metadata": {"action": "open_settings"},
        }


class ClearChatTool(ToolBase):
    name = "ui.clear_chat"
    description = "Limpar a conversa atual"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "data": {"chat_cleared": True},
            "metadata": {"action": "clear_chat"},
        }


class SetVoiceEnabledTool(ToolBase):
    name = "ui.set_voice_enabled"
    description = "Ativar ou desativar a voz"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        enabled = input_data.get("enabled", True)
        return {
            "data": {"voice_enabled": enabled},
            "metadata": {"action": "set_voice_enabled", "enabled": enabled},
        }


class SetAutoSpeakTool(ToolBase):
    name = "ui.set_auto_speak"
    description = "Ativar ou desativar auto speak"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        enabled = input_data.get("enabled", True)
        return {
            "data": {"auto_speak": enabled},
            "metadata": {"action": "set_auto_speak", "enabled": enabled},
        }


class SetVoiceProfileTool(ToolBase):
    name = "ui.set_voice_profile"
    description = "Configurar perfil de voz"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "data": {
                "voice_name": input_data.get("voice_name", ""),
                "rate": input_data.get("rate", 1.0),
                "pitch": input_data.get("pitch", 1.1),
            },
            "metadata": {"action": "set_voice_profile"},
        }
