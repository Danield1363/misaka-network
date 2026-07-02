from __future__ import annotations
import logging
from typing import Any
from datetime import datetime, timezone
from app.services.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class ApprovalRepository:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            return {"id": "local", **data}
        result = self.client.table("action_approvals").insert(data).execute()
        return result.data[0] if result.data else {}

    async def list_pending(self) -> list[dict[str, Any]]:
        if self.client is None:
            return []
        result = self.client.table("action_approvals").select("*").eq("status", "pending").order("created_at", desc=True).execute()
        return result.data or []

    async def approve(self, approval_id: str) -> dict[str, Any] | None:
        if self.client is None:
            return None
        data = {
            "status": "approved",
            "approved_at": datetime.now(timezone.utc).isoformat(),
        }
        result = self.client.table("action_approvals").update(data).eq("id", approval_id).execute()
        return result.data[0] if result.data else None

    async def deny(self, approval_id: str) -> dict[str, Any] | None:
        if self.client is None:
            return None
        data = {
            "status": "denied",
            "denied_at": datetime.now(timezone.utc).isoformat(),
        }
        result = self.client.table("action_approvals").update(data).eq("id", approval_id).execute()
        return result.data[0] if result.data else None
