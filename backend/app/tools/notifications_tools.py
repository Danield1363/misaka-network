from typing import Any
from app.tools.base import ToolBase


class ListAlertsTool(ToolBase):
    name = "notifications.list_alerts"
    description = "Listar alertas importantes"
    category = "notifications"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.notifications.engine import NotificationEngine
        engine = NotificationEngine()
        alerts = await engine.list_important_alerts()
        return {
            "data": {"alerts": alerts, "total": len(alerts)},
            "metadata": {"total": len(alerts)},
        }


class AckAlertTool(ToolBase):
    name = "notifications.ack_alert"
    description = "Marcar um alerta como visto"
    category = "notifications"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.notifications.engine import NotificationEngine
        engine = NotificationEngine()
        alert_id = input_data.get("alert_id", "")
        result = await engine.acknowledge_alert(alert_id)
        return {
            "data": {"acknowledged": result is not None},
            "metadata": {"alert_id": alert_id},
        }


class AckAllAlertsTool(ToolBase):
    name = "notifications.ack_all_alerts"
    description = "Marcar todos os alertas pendentes como vistos"
    category = "notifications"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.notifications.engine import NotificationEngine
        engine = NotificationEngine()
        alerts = await engine.list_important_alerts("pending")
        acked = 0
        for alert in alerts:
            alert_id = alert.get("id")
            if alert_id:
                result = await engine.acknowledge_alert(alert_id)
                if result:
                    acked += 1
        return {
            "data": {"acked_count": acked, "total_pending": len(alerts)},
            "metadata": {"acked_count": acked},
        }


class ClearResolvedAlertsTool(ToolBase):
    name = "notifications.clear_resolved_alerts"
    description = "Limpar alertas já resolvidos"
    category = "notifications"
    danger_level = "medium"
    requires_confirmation = True

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.notifications.engine import NotificationEngine
        engine = NotificationEngine()
        alerts = await engine.list_important_alerts("acknowledged")
        return {
            "data": {"cleared": len(alerts)},
            "metadata": {"cleared_count": len(alerts)},
        }


class NotificationsSummaryTool(ToolBase):
    name = "notifications.summary"
    description = "Resumo das notificações"
    category = "notifications"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        from app.notifications.engine import NotificationEngine
        engine = NotificationEngine()
        pending = await engine.list_important_alerts("pending")
        critical = len([a for a in pending if a.get("priority") == "critical"])
        important = len([a for a in pending if a.get("priority") == "important"])
        return {
            "data": {
                "total_pending": len(pending),
                "critical": critical,
                "important": important,
            },
            "metadata": {},
        }
