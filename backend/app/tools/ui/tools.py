from typing import Any
from app.tools.base import ToolBase


class SetHudModeTool(ToolBase):
    name = "ui.set_hud_mode"
    description = "Ativa ou desativa o modo HUD"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        enabled = input_data.get("enabled", True)
        return {
            "data": {"hud_enabled": enabled},
            "metadata": {"tool": self.name, "action": "set_hud_mode"}
        }


class OpenSettingsTool(ToolBase):
    name = "ui.open_settings"
    description = "Abre o painel de configurações"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "data": {"action": "open_settings"},
            "metadata": {"tool": self.name}
        }


class ClearChatTool(ToolBase):
    name = "ui.clear_chat"
    description = "Limpa o histórico do chat"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "data": {"action": "clear_chat"},
            "metadata": {"tool": self.name}
        }


class SetVoiceEnabledTool(ToolBase):
    name = "ui.set_voice_enabled"
    description = "Ativa ou desativa a voz da Misaka"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        enabled = input_data.get("enabled", True)
        return {
            "data": {"voice_enabled": enabled},
            "metadata": {"tool": self.name}
        }


class SetAutoSpeakTool(ToolBase):
    name = "ui.set_auto_speak"
    description = "Ativa ou desativa a fala automática"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        enabled = input_data.get("enabled", True)
        return {
            "data": {"auto_speak": enabled},
            "metadata": {"tool": self.name}
        }


class SetVoiceProfileTool(ToolBase):
    name = "ui.set_voice_profile"
    description = "Muda o perfil de voz (feminina, suave, sistema, rápida)"
    category = "ui"
    danger_level = "safe"
    requires_confirmation = False

    PROFILES = {
        "feminine": {"name": "Misaka BR Feminina", "pitch": 1.15, "rate": 1.0},
        "soft": {"name": "Misaka Suave", "pitch": 1.08, "rate": 0.9},
        "system": {"name": "Misaka Sistema", "pitch": 1.0, "rate": 1.05},
        "fast": {"name": "Misaka Rápida", "pitch": 1.1, "rate": 1.3},
    }

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        profile = input_data.get("profile", "feminine")
        profile_config = self.PROFILES.get(profile, self.PROFILES["feminine"])
        return {
            "data": {"profile": profile, "config": profile_config},
            "metadata": {"tool": self.name}
        }
