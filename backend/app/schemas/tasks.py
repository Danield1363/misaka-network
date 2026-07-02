from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Título da tarefa")
    description: str | None = Field(None, description="Descrição da tarefa")
    priority: int = Field(3, ge=1, le=5, description="Prioridade (1-5)")
    due_at: datetime | None = Field(None, description="Data de vencimento")
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1)
    description: str | None = None
    status: str | None = Field(None, pattern="^(pending|in_progress|done|cancelled)$")
    priority: int | None = Field(None, ge=1, le=5)
    due_at: datetime | None = None
    metadata: dict[str, Any] | None = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None
    status: str
    priority: int
    due_at: str | None
    metadata: dict[str, Any]
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int