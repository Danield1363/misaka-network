from typing import Any
from app.tools.base import ToolBase


class DesktopOpenAppTool(ToolBase):
    name = "desktop.open_app"
    description = "Abre um aplicativo no PC (navegador, Discord, VS Code, Explorer)"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        app_name = input_data.get("app", "browser")
        return {
            "data": {"action": "open_app", "app": app_name},
            "metadata": {"tool": self.name, "requires_desktop_bridge": True}
        }


class DesktopOpenUrlTool(ToolBase):
    name = "desktop.open_url"
    description = "Abre uma URL no navegador padrão"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        url = input_data.get("url", "https://www.google.com")
        return {
            "data": {"action": "open_url", "url": url},
            "metadata": {"tool": self.name, "requires_desktop_bridge": True}
        }


class DesktopSearchWebTool(ToolBase):
    name = "desktop.search_web"
    description = "Pesquisa algo no Google"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        query = input_data.get("query", "")
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}" if query else "https://www.google.com"
        return {
            "data": {"action": "search_web", "query": query, "url": url},
            "metadata": {"tool": self.name, "requires_desktop_bridge": True}
        }


class DesktopGetSystemStatusTool(ToolBase):
    name = "desktop.get_system_status"
    description = "Obtém informações do sistema (CPU, RAM, disco)"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "data": {"action": "get_system_status"},
            "metadata": {"tool": self.name, "requires_desktop_bridge": True}
        }


class DesktopSetVolumeTool(ToolBase):
    name = "desktop.set_volume"
    description = "Ajusta o volume do sistema"
    category = "desktop"
    danger_level = "medium"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        level = input_data.get("level", 50)
        return {
            "data": {"action": "set_volume", "level": level},
            "metadata": {"tool": self.name, "requires_desktop_bridge": True}
        }


class DesktopShowNotificationTool(ToolBase):
    name = "desktop.show_notification"
    description = "Mostra uma notificação nativa no PC"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        title = input_data.get("title", "Misaka")
        body = input_data.get("body", "")
        return {
            "data": {"action": "show_notification", "title": title, "body": body},
            "metadata": {"tool": self.name, "requires_desktop_bridge": True}
        }


class DesktopFocusMisakaTool(ToolBase):
    name = "desktop.focus_misaka"
    description = "Foca a janela da Misaka"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "data": {"action": "focus_misaka"},
            "metadata": {"tool": self.name, "requires_desktop_bridge": True}
        }


class DesktopToggleAlwaysOnTopTool(ToolBase):
    name = "desktop.toggle_always_on_top"
    description = "Alterna o modo sempre no topo"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        enabled = input_data.get("enabled", True)
        return {
            "data": {"action": "toggle_always_on_top", "enabled": enabled},
            "metadata": {"tool": self.name, "requires_desktop_bridge": True}
        }


class DesktopToggleHudModeTool(ToolBase):
    name = "desktop.toggle_hud_mode"
    description = "Alterna o modo HUD no desktop"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        enabled = input_data.get("enabled", True)
        return {
            "data": {"action": "toggle_hud_mode", "enabled": enabled},
            "metadata": {"tool": self.name, "requires_desktop_bridge": True}
        }
