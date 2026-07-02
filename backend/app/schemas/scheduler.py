from pydantic import BaseModel


class SchedulerRunResponse(BaseModel):
    processed_reminders: int
    created_notifications: int
    status: str


class NotificationOutboxResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    status: str
    target: str
    scheduled_for: str | None
    sent_at: str | None
    created_at: str


class NotificationListResponse(BaseModel):
    notifications: list[NotificationOutboxResponse]
    total: int