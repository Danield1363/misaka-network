import logging
import time
from datetime import datetime, timezone
from typing import Any
from app.bridge.rate_limit import rate_limiter, deduplicator
from app.notifications.engine import NotificationEngine
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class NotificationBridge:
    def __init__(self) -> None:
        self.engine = NotificationEngine()
        self.settings = get_settings()
        self._notifications_today: int = 0
        self._last_notification: str | None = None
        self._connected_devices: set[str] = set()

    def verify_token(self, token: str | None) -> bool:
        if self.settings.ENVIRONMENT == "production":
            if not self.settings.NOTIFICATION_INGEST_TOKEN:
                logger.error("NOTIFICATION_INGEST_TOKEN not configured in production")
                return False
            return token == self.settings.NOTIFICATION_INGEST_TOKEN
        return True

    async def ingest(self, data: dict[str, Any]) -> dict[str, Any]:
        device_id = data.get("device_id", "unknown")
        self._connected_devices.add(device_id)
        self._last_notification = datetime.now(timezone.utc).isoformat()
        self._notifications_today += 1

        if not rate_limiter.is_allowed(device_id):
            retry_after = rate_limiter.get_retry_after(device_id)
            logger.warning(f"Rate limited device={device_id} retry_after={retry_after}")
            return {
                "status": "rate_limited",
                "error": "Rate limit exceeded",
                "retry_after": retry_after
            }

        is_duplicate = deduplicator.is_duplicate(data)
        if is_duplicate:
            logger.info(f"Duplicate notification app={data.get('app_name')} title={data.get('title')}")
            return {
                "status": "duplicate",
                "duplicate": True,
                "message": "Notification already received"
            }

        result = await self.engine.ingest_notification(data)

        logger.info(
            f"Notification ingested app={data.get('app_name')} "
            f"title={data.get('title')} "
            f"importance={result.get('importance')} "
            f"should_alert={result.get('should_alert')} "
            f"category={result.get('category')}"
        )

        return {
            "status": "received",
            "notification_id": None,
            "duplicate": False,
            "importance": result.get("importance"),
            "should_alert": result.get("should_alert"),
            "summary": result.get("summary"),
            "category": result.get("category"),
            "is_sensitive": result.get("is_sensitive")
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "bridge_status": "online",
            "connected_devices": len(self._connected_devices),
            "last_notification": self._last_notification,
            "notifications_today": self._notifications_today,
            "token_required": self.settings.ENVIRONMENT == "production"
        }


notification_bridge = NotificationBridge()