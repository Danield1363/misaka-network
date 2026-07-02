from typing import Any
from app.tools.base import ToolBase


class DesktopOpenAppTool(ToolBase):
    name = "desktop.open_app"
    description = "Abrir um aplicativo no desktop"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        app_name = input_data.get("app_name", "")
        return {
            "data": {"app_name": app_name, "action": "open"},
            "metadata": {"action": "open_app", "app": app_name, "platform": "desktop"},
        }


class DesktopOpenUrlTool(ToolBase):
    name = "desktop.open_url"
    description = "Abrir uma URL no navegador"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        url = input_data.get("url", "")
        return {
            "data": {"url": url, "action": "open_url"},
            "metadata": {"action": "open_url", "url": url},
        }


class DesktopSearchWebTool(ToolBase):
    name = "desktop.search_web"
    description = "Pesquisar na web"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        query = input_data.get("query", "")
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return {
            "data": {"query": query, "url": url},
            "metadata": {"action": "search_web", "query": query},
        }


class DesktopGetSystemStatusTool(ToolBase):
    name = "desktop.get_system_status"
    description = "Obter status do sistema"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        import platform
        import os
        return {
            "data": {
                "platform": platform.system(),
                "hostname": platform.node(),
                "pid": os.getpid(),
            },
            "metadata": {"action": "get_system_status"},
        }


class DesktopSetVolumeTool(ToolBase):
    name = "desktop.set_volume"
    description = "Ajustar volume do sistema"
    category = "desktop"
    danger_level = "medium"
    requires_confirmation = True

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        level = input_data.get("level", 50)
        return {
            "data": {"volume": level},
            "metadata": {"action": "set_volume", "level": level},
        }


class DesktopShowNotificationTool(ToolBase):
    name = "desktop.show_notification"
    description = "Mostrar notificação no desktop"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        title = input_data.get("title", "Misaka")
        body = input_data.get("body", "")
        return {
            "data": {"title": title, "body": body, "shown": True},
            "metadata": {"action": "show_notification"},
        }


class DesktopFocusMisakaTool(ToolBase):
    name = "desktop.focus_misaka"
    description = "Focar janela do Misaka"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "data": {"focused": True},
            "metadata": {"action": "focus_misaka"},
        }


class DesktopToggleAlwaysOnTopTool(ToolBase):
    name = "desktop.toggle_always_on_top"
    description = "Alternar sempre no topo"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        enabled = input_data.get("enabled", True)
        return {
            "data": {"always_on_top": enabled},
            "metadata": {"action": "toggle_always_on_top", "enabled": enabled},
        }


class DesktopToggleHudModeTool(ToolBase):
    name = "desktop.toggle_hud_mode"
    description = "Alternar modo HUD no desktop"
    category = "desktop"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        enabled = input_data.get("enabled", False)
        return {
            "data": {"hud_mode": enabled},
            "metadata": {"action": "toggle_hud_mode", "enabled": enabled},
        }
