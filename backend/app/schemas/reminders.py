from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime


class ReminderCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Título do lembrete")
    description: str | None = Field(None, description="Descrição do lembrete")
    remind_at: datetime = Field(..., description="Data/hora do lembrete (UTC)")
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReminderUpdate(BaseModel):
    title: str | None = Field(None, min_length=1)
    description: str | None = None
    remind_at: datetime | None = None
    status: str | None = Field(None, pattern="^(pending|triggered|done|cancelled)$")
    metadata: dict[str, Any] | None = None


class ReminderResponse(BaseModel):
    id: str
    title: str
    description: str | None
    remind_at: str
    status: str
    source: str
    metadata: dict[str, Any]
    created_at: str
    updated_at: str


class ReminderListResponse(BaseModel):
    reminders: list[ReminderResponse]
    total: int