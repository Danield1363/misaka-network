import logging
from typing import Any
from app.approvals.repository import ApprovalRepository
from app.services.supabase import is_memory_enabled

logger = logging.getLogger(__name__)


class ApprovalEngine:
    def __init__(self) -> None:
        self.repository = ApprovalRepository()
        self.enabled = is_memory_enabled()

    async def create_approval(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {"id": "local", "status": "pending", **data}
        try:
            data["status"] = "pending"
            return await self.repository.create(data)
        except Exception as e:
            logger.error(f"Failed to create approval: {e}")
            return {"id": "local", "status": "error", "error": str(e)}

    async def get_pending_approvals(self) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            return await self.repository.list_pending()
        except Exception as e:
            logger.error(f"Failed to list pending approvals: {e}")
            return []

    async def approve(self, approval_id: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        try:
            return await self.repository.approve(approval_id)
        except Exception as e:
            logger.error(f"Failed to approve: {e}")
            return None

    async def deny(self, approval_id: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        try:
            return await self.repository.deny(approval_id)
        except Exception as e:
            logger.error(f"Failed to deny: {e}")
            return None
