from typing import Any
from app.tools.base import ToolBase


class AndroidEnqueueActionTool(ToolBase):
    name = "android.enqueue_action"
    description = "Enfileirar ação para o celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.android.engine import AndroidEngine
        engine = AndroidEngine()
        result = await engine.enqueue_action(input_data)
        return {
            "data": result,
            "metadata": {"action": "enqueue", "action_type": input_data.get("action_type", "")},
        }


class AndroidListPendingTool(ToolBase):
    name = "android.list_pending_actions"
    description = "Listar ações pendentes do celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.android.engine import AndroidEngine
        engine = AndroidEngine()
        actions = await engine.list_pending_actions()
        return {
            "data": {"actions": actions, "total": len(actions)},
            "metadata": {"total_pending": len(actions)},
        }


class AndroidCancelActionTool(ToolBase):
    name = "android.cancel_action"
    description = "Cancelar ação pendente do celular"
    category = "android"
    danger_level = "medium"
    requires_confirmation = True

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.android.engine import AndroidEngine
        engine = AndroidEngine()
        action_id = input_data.get("action_id", "")
        result = await engine.cancel_action(action_id)
        return {
            "data": {"cancelled": result},
            "metadata": {"action_id": action_id},
        }


class AndroidPingDeviceTool(ToolBase):
    name = "android.ping_device"
    description = "Verificar conexão com o celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.android.engine import AndroidEngine
        engine = AndroidEngine()
        status = await engine.get_status()
        return {
            "data": status,
            "metadata": {"action": "ping"},
        }


class AndroidShowToastTool(ToolBase):
    name = "android.show_toast"
    description = "Mostrar toast no celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.android.engine import AndroidEngine
        engine = AndroidEngine()
        message = input_data.get("message", "Misaka")
        result = await engine.enqueue_action({
            "action_type": "show_toast",
            "payload": {"message": message},
            "risk_level": "safe",
        })
        return {
            "data": {"enqueued": True, "message": message},
            "metadata": {"action": "show_toast"},
        }


class AndroidVibrateTool(ToolBase):
    name = "android.vibrate"
    description = "Fazer celular vibrar"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.android.engine import AndroidEngine
        engine = AndroidEngine()
        result = await engine.enqueue_action({
            "action_type": "vibrate",
            "payload": {"duration": input_data.get("duration", 500)},
            "risk_level": "safe",
        })
        return {
            "data": {"enqueued": True},
            "metadata": {"action": "vibrate"},
        }


class AndroidOpenAppTool(ToolBase):
    name = "android.open_app"
    description = "Abrir app no celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.android.engine import AndroidEngine
        engine = AndroidEngine()
        package_name = input_data.get("package_name", "")
        result = await engine.enqueue_action({
            "action_type": "open_app",
            "payload": {"package_name": package_name},
            "risk_level": "safe",
        })
        return {
            "data": {"enqueued": True, "package_name": package_name},
            "metadata": {"action": "open_app"},
        }


class AndroidOpenUrlTool(ToolBase):
    name = "android.open_url"
    description = "Abrir URL no celular"
    category = "android"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.android.engine import AndroidEngine
        engine = AndroidEngine()
        url = input_data.get("url", "")
        result = await engine.enqueue_action({
            "action_type": "open_url",
            "payload": {"url": url},
            "risk_level": "safe",
        })
        return {
            "data": {"enqueued": True, "url": url},
            "metadata": {"action": "open_url"},
        }
