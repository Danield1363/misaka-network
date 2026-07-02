import logging
from typing import Any
from app.actions.repository import ActionRepository
from app.services.supabase import is_memory_enabled

logger = logging.getLogger(__name__)


class ActionEngine:
    def __init__(self) -> None:
        self.repository = ActionRepository()
        self.enabled = is_memory_enabled()

    async def log_action_start(
        self,
        action_name: str,
        tool_name: str | None = None,
        agent_name: str | None = None,
        input_data: dict[str, Any] | None = None,
        dry_run: bool = False,
        requires_confirmation: bool = False
    ) -> dict[str, Any]:
        if not self.enabled:
            return {"id": "local", "status": "pending"}
        try:
            data = {
                "action_name": action_name,
                "tool_name": tool_name,
                "agent_name": agent_name,
                "status": "pending",
                "input": input_data or {},
                "output": {},
                "dry_run": dry_run,
                "requires_confirmation": requires_confirmation,
                "confirmed": False,
                "metadata": {}
            }
            return await self.repository.create(data)
        except Exception as e:
            logger.error(f"Failed to log action start: {e}")
            return {"id": "local", "status": "pending"}

    async def log_action_success(
        self,
        action_id: str | None,
        output: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if not self.enabled or not action_id or action_id == "local":
            return {"id": action_id, "status": "success"}
        try:
            data = {
                "status": "success",
                "output": output or {},
                "metadata": metadata or {},
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            return await self.repository.update(action_id, data) or {"id": action_id, "status": "success"}
        except Exception as e:
            logger.error(f"Failed to log action success: {e}")
            return {"id": action_id, "status": "success"}

    async def log_action_error(
        self,
        action_id: str | None,
        error: str = "",
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if not self.enabled or not action_id or action_id == "local":
            return {"id": action_id, "status": "failed"}
        try:
            data = {
                "status": "failed",
                "output": {},
                "error": error,
                "metadata": metadata or {},
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            return await self.repository.update(action_id, data) or {"id": action_id, "status": "failed"}
        except Exception as e:
            logger.error(f"Failed to log action error: {e}")
            return {"id": action_id, "status": "failed"}

    async def list_action_logs(self, status: str | None = None) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            return await self.repository.list(status)
        except Exception as e:
            logger.error(f"Failed to list action logs: {e}")
            return []

    async def get_action_log(self, action_id: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        try:
            return await self.repository.get(action_id)
        except Exception as e:
            logger.error(f"Failed to get action log: {e}")
            return None