import logging
from typing import Any
from datetime import datetime, timezone
from app.notifications.repository import NotificationRepository
from app.notifications.classifier import NotificationClassifier
from app.services.supabase import is_notifications_enabled

logger = logging.getLogger(__name__)


class NotificationEngine:
    def __init__(self) -> None:
        self.repository = NotificationRepository()
        self.classifier = NotificationClassifier()
        self.enabled = is_notifications_enabled()

    async def ingest_notification(self, data: dict[str, Any]) -> dict[str, Any]:
        classification = self.classifier.classify(data)

        notification_record = {
            "app_name": data.get("app_name", ""),
            "package_name": data.get("package_name"),
            "title": data.get("title"),
            "content": data.get("content"),
            "sender": data.get("sender"),
            "channel": data.get("channel"),
            "received_at": data.get("received_at", datetime.now(timezone.utc).isoformat()),
            "importance": classification["importance"],
            "category": classification["category"],
            "is_sensitive": classification["is_sensitive"],
            "should_alert": classification["should_alert"],
            "summary": classification["summary"],
            "metadata": data.get("metadata", {}),
        }

        persistence_failed = False

        try:
            saved = await self.repository.create(notification_record)
        except Exception as e:
            logger.error(f"Failed to save notification: app={data.get('app_name')} error={type(e).__name__}")
            persistence_failed = True
            saved = {"id": None}

        if classification["should_alert"]:
            try:
                alert_data = {
                    "notification_id": saved.get("id"),
                    "title": f"{classification['importance'].upper()}: {data.get('app_name', '')}",
                    "message": classification["summary"],
                    "status": "pending",
                    "priority": classification["importance"],
                }
                await self.repository.create_alert(alert_data)
            except Exception as e:
                logger.error(f"Failed to save alert: app={data.get('app_name')} error={type(e).__name__}")
                persistence_failed = True

        classification["persistence_failed"] = persistence_failed

        return classification

    async def list_notifications(self, importance: str | None = None) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            return await self.repository.list(importance)
        except Exception as e:
            logger.error(f"Failed to list notifications: {e}")
            return []

    async def list_important_alerts(self, status: str | None = None) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            return await self.repository.list_alerts(status)
        except Exception as e:
            logger.error(f"Failed to list alerts: {e}")
            return []

    async def acknowledge_alert(self, alert_id: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        try:
            return await self.repository.acknowledge_alert(alert_id)
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return None

    async def acknowledge_all_alerts(self) -> int:
        if not self.enabled:
            return 0
        try:
            alerts = await self.repository.list_alerts("pending")
            acked = 0
            for alert in alerts:
                alert_id = alert.get("id")
                if alert_id:
                    result = await self.repository.acknowledge_alert(alert_id)
                    if result:
                        acked += 1
            return acked
        except Exception as e:
            logger.error(f"Failed to acknowledge all alerts: {e}")
            return 0

    async def get_summary(self) -> dict[str, int]:
        if not self.enabled:
            return {"total_pending": 0, "critical": 0, "important": 0}
        try:
            alerts = await self.repository.list_alerts("pending")
            critical = len([a for a in alerts if a.get("priority") == "critical"])
            important = len([a for a in alerts if a.get("priority") == "important"])
            return {
                "total_pending": len(alerts),
                "critical": critical,
                "important": important,
            }
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return {"total_pending": 0, "critical": 0, "important": 0}
