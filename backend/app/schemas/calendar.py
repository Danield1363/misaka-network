from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from typing import Any
from datetime import datetime


class CalendarEventCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Título do evento")
    description: str | None = Field(None, description="Descrição do evento")
    location: str | None = Field(None, description="Local do evento")
    starts_at: datetime = Field(..., description="Data/hora de início (UTC)")
    ends_at: datetime | None = Field(None, description="Data/hora de término (UTC)")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_ends_at(self) -> CalendarEventCreate:
        if self.ends_at and self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class CalendarEventUpdate(BaseModel):
    title: str | None = Field(None, min_length=1)
    description: str | None = None
    location: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: str | None = Field(None, pattern="^(scheduled|cancelled|done)$")
    metadata: dict[str, Any] | None = None


class CalendarEventResponse(BaseModel):
    id: str
    title: str
    description: str | None
    location: str | None
    starts_at: str
    ends_at: str | None
    status: str
    source: str
    metadata: dict[str, Any]
    created_at: str
    updated_at: str


class CalendarEventListResponse(BaseModel):
    events: list[CalendarEventResponse]
    total: int