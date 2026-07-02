from typing import Any
from app.tools.base import ToolBase
from app.notifications.engine import NotificationEngine


class ListAlertsTool(ToolBase):
    name = "notifications.list_alerts"
    description = "Lista alertas importantes ativos"
    category = "notifications"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        engine = NotificationEngine()
        alerts = await engine.list_important_alerts()
        return {
            "data": {"alerts": alerts, "total": len(alerts)},
            "metadata": {"tool": self.name}
        }


class AckAlertTool(ToolBase):
    name = "notifications.ack_alert"
    description = "Marca um alerta específico como visto"
    category = "notifications"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        engine = NotificationEngine()
        alert_id = input_data.get("alert_id", "")
        result = await engine.acknowledge_alert(alert_id)
        return {
            "data": {"acknowledged": result is not None, "alert_id": alert_id},
            "metadata": {"tool": self.name}
        }


class AckAllAlertsTool(ToolBase):
    name = "notifications.ack_all_alerts"
    description = "Marca todos os alertas pendentes como vistos"
    category = "notifications"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        engine = NotificationEngine()
        alerts = await engine.list_important_alerts("pending")
        acked = 0
        for alert in alerts:
            result = await engine.acknowledge_alert(alert["id"])
            if result:
                acked += 1
        return {
            "data": {"acknowledged_count": acked, "total_pending": len(alerts)},
            "metadata": {"tool": self.name}
        }


class ClearResolvedAlertsTool(ToolBase):
    name = "notifications.clear_resolved_alerts"
    description = "Remove alertas já resolvidos/vistos do histórico"
    category = "notifications"
    danger_level = "medium"
    requires_confirmation = True

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        engine = NotificationEngine()
        alerts = await engine.list_important_alerts("acknowledged")
        return {
            "data": {"resolved_count": len(alerts), "message": "Alertas resolvidos identificados"},
            "metadata": {"tool": self.name}
        }


class NotificationSummaryTool(ToolBase):
    name = "notifications.summary"
    description = "Retorna um resumo das notificações e alertas"
    category = "notifications"
    danger_level = "safe"
    requires_confirmation = False

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        engine = NotificationEngine()
        all_alerts = await engine.list_important_alerts()
        pending = [a for a in all_alerts if a.get("status") == "pending"]
        critical = [a for a in all_alerts if a.get("priority") == "critical"]
        return {
            "data": {
                "total": len(all_alerts),
                "pending": len(pending),
                "critical": len(critical),
            },
            "metadata": {"tool": self.name}
        }
