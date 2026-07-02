from pydantic import BaseModel, Field
from typing import Any


class ToolInfo(BaseModel):
    name: str
    description: str
    category: str
    danger_level: str
    requires_confirmation: bool


class ToolListResponse(BaseModel):
    tools: list[ToolInfo]


class ToolExecuteRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    input_data: dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = Field(False, description="Run in dry-run mode")
    confirmed: bool = Field(False, description="Confirm execution")
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolExecuteResponse(BaseModel):
    success: bool
    tool: str
    dry_run: bool = False
    requires_confirmation: bool = False
    data: dict[str, Any] = {}
    error: str | None = None
    metadata: dict[str, Any] = {}