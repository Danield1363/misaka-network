from pydantic import BaseModel
from typing import Any
from datetime import datetime


class ActionLogResponse(BaseModel):
    id: str | None = None
    action_name: str
    tool_name: str | None = None
    agent_name: str | None = None
    status: str
    input: dict[str, Any] = {}
    output: dict[str, Any] = {}
    error: str | None = None
    dry_run: bool = False
    requires_confirmation: bool = False
    confirmed: bool = False
    metadata: dict[str, Any] = {}
    created_at: str | None = None
    completed_at: str | None = None


class ActionLogListResponse(BaseModel):
    logs: list[ActionLogResponse]
    total: int