from typing import Any
from app.tools.base import ToolBase


class AndroidEnqueueActionTool(ToolBase):
    name = "android.enqueue_action"
    description = "Enfileira uma ação para ser executada no celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        action_type = input_data.get("action_type", "")
        payload = input_data.get("payload", {})
        return {
            "data": {
                "action_id": f"act_{hash(str(input_data)) % 10000}",
                "action_type": action_type,
                "payload": payload,
                "status": "pending"
            },
            "metadata": {"tool": self.name}
        }


class AndroidListPendingActionsTool(ToolBase):
    name = "android.list_pending_actions"
    description = "Lista ações pendentes no celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "data": {"actions": [], "total": 0},
            "metadata": {"tool": self.name}
        }


class AndroidCancelActionTool(ToolBase):
    name = "android.cancel_action"
    description = "Cancela uma ação pendente no celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        action_id = input_data.get("action_id", "")
        return {
            "data": {"action_id": action_id, "cancelled": True},
            "metadata": {"tool": self.name}
        }


class AndroidPingDeviceTool(ToolBase):
    name = "android.ping_device"
    description = "Verifica se o celular está conectado"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "data": {"connected": False, "message": "Bridge não conectado"},
            "metadata": {"tool": self.name}
        }


class AndroidShowToastTool(ToolBase):
    name = "android.show_toast"
    description = "Mostra uma mensagem Toast no celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        message = input_data.get("message", "Misaka")
        return {
            "data": {"action": "show_toast", "message": message, "status": "enqueued"},
            "metadata": {"tool": self.name}
        }


class AndroidVibrateTool(ToolBase):
    name = "android.vibrate"
    description = "Faz o celular vibrar"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        duration = input_data.get("duration_ms", 500)
        return {
            "data": {"action": "vibrate", "duration_ms": duration, "status": "enqueued"},
            "metadata": {"tool": self.name}
        }


class AndroidOpenAppTool(ToolBase):
    name = "android.open_app"
    description = "Abre um app no celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        package = input_data.get("package", "")
        return {
            "data": {"action": "open_app", "package": package, "status": "enqueued"},
            "metadata": {"tool": self.name}
        }


class AndroidOpenUrlTool(ToolBase):
    name = "android.open_url"
    description = "Abre uma URL no celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        url = input_data.get("url", "")
        return {
            "data": {"action": "open_url", "url": url, "status": "enqueued"},
            "metadata": {"tool": self.name}
        }
