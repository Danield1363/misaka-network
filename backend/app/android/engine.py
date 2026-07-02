import logging
from typing import Any
from app.android.repository import AndroidRepository
from app.core.config import get_settings
from app.services.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class AndroidEngine:
    def __init__(self) -> None:
        self.repository = AndroidRepository()
        self.settings = get_settings()
        self.bridge_enabled = self.settings.ANDROID_BRIDGE_ENABLED
        self.db_configured = bool(self.settings.SUPABASE_URL and self.settings.SUPABASE_SERVICE_ROLE_KEY)

    async def enqueue_action(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self.bridge_enabled:
            return {"id": "local", "status": "error", "error": "Android bridge is disabled. Set ANDROID_BRIDGE_ENABLED=true."}
        if not self.db_configured:
            return {"id": "local", "status": "error", "error": "Android bridge enabled, but database not configured."}
        try:
            data["status"] = "pending"
            return await self.repository.create(data)
        except Exception as e:
            logger.error(f"Failed to enqueue action: {e}")
            return {"id": "local", "status": "error", "error": str(e)}

    async def list_pending_actions(self) -> list[dict[str, Any]]:
        if not self.bridge_enabled or not self.db_configured:
            return []
        try:
            return await self.repository.list_pending()
        except Exception as e:
            logger.error(f"Failed to list pending actions: {e}")
            return []

    async def complete_action(self, action_id: str, result: dict[str, Any] | None = None) -> bool:
        if not self.bridge_enabled or not self.db_configured:
            return False
        try:
            return await self.repository.complete(action_id, result)
        except Exception as e:
            logger.error(f"Failed to complete action: {e}")
            return False

    async def fail_action(self, action_id: str, error_message: str = "") -> bool:
        if not self.bridge_enabled or not self.db_configured:
            return False
        try:
            return await self.repository.fail(action_id, error_message)
        except Exception as e:
            logger.error(f"Failed to fail action: {e}")
            return False

    async def cancel_action(self, action_id: str) -> bool:
        if not self.bridge_enabled or not self.db_configured:
            return False
        try:
            return await self.repository.cancel(action_id)
        except Exception as e:
            logger.error(f"Failed to cancel action: {e}")
            return False

    async def get_status(self) -> dict[str, Any]:
        if not self.bridge_enabled:
            return {
                "enabled": False,
                "connected": False,
                "pending_actions": 0,
                "last_connection": None,
                "reason": "Android bridge disabled. Set ANDROID_BRIDGE_ENABLED=true.",
            }
        if not self.db_configured:
            return {
                "enabled": True,
                "connected": False,
                "pending_actions": 0,
                "last_connection": None,
                "reason": "Database not configured.",
            }
        try:
            pending = await self.list_pending_actions()
            return {
                "enabled": True,
                "connected": len(pending) >= 0,
                "pending_actions": len(pending),
                "last_connection": None,
            }
        except Exception:
            return {
                "enabled": True,
                "connected": False,
                "pending_actions": 0,
                "last_connection": None,
            }
