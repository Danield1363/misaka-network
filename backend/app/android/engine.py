import logging
from typing import Any
from app.android.repository import AndroidRepository
from app.services.supabase import is_memory_enabled

logger = logging.getLogger(__name__)


class AndroidEngine:
    def __init__(self) -> None:
        self.repository = AndroidRepository()
        self.enabled = is_memory_enabled()

    async def enqueue_action(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {"id": "local", "status": "pending", "message": "Database not configured"}
        try:
            data["status"] = "pending"
            return await self.repository.create(data)
        except Exception as e:
            logger.error(f"Failed to enqueue action: {e}")
            return {"id": "local", "status": "error", "error": str(e)}

    async def list_pending_actions(self) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            return await self.repository.list_pending()
        except Exception as e:
            logger.error(f"Failed to list pending actions: {e}")
            return []

    async def complete_action(self, action_id: str, result: dict[str, Any] | None = None) -> bool:
        if not self.enabled:
            return False
        try:
            return await self.repository.complete(action_id, result)
        except Exception as e:
            logger.error(f"Failed to complete action: {e}")
            return False

    async def fail_action(self, action_id: str, error_message: str = "") -> bool:
        if not self.enabled:
            return False
        try:
            return await self.repository.fail(action_id, error_message)
        except Exception as e:
            logger.error(f"Failed to fail action: {e}")
            return False

    async def cancel_action(self, action_id: str) -> bool:
        if not self.enabled:
            return False
        try:
            return await self.repository.cancel(action_id)
        except Exception as e:
            logger.error(f"Failed to cancel action: {e}")
            return False

    async def get_status(self) -> dict[str, Any]:
        if not self.enabled:
            return {
                "enabled": False,
                "connected": False,
                "pending_actions": 0,
                "last_connection": None,
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
