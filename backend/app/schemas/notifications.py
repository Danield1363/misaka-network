from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime


class NotificationIngestRequest(BaseModel):
    app_name: str = Field(..., min_length=1, description="App name")
    package_name: str | None = None
    title: str | None = None
    content: str | None = None
    sender: str | None = None
    channel: str | None = None
    received_at: datetime = Field(..., description="When notification was received")
    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    id: str | None = None
    app_name: str
    title: str | None = None
    content: str | None = None
    sender: str | None = None
    importance: str
    category: str
    is_sensitive: bool
    should_alert: bool
    summary: str | None = None
    received_at: str
    created_at: str | None = None


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int


class ImportantAlertResponse(BaseModel):
    id: str | None = None
    notification_id: str | None = None
    title: str
    message: str
    status: str
    priority: str
    created_at: str | None = None
    acknowledged_at: str | None = None


class AlertListResponse(BaseModel):
    alerts: list[ImportantAlertResponse]
    total: int


class NotificationIngestResponse(BaseModel):
    importance: str
    should_alert: bool
    summary: str
    category: str
    is_sensitive: bool