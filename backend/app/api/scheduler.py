from __future__ import annotations
from fastapi import APIRouter, Query
from app.schemas.scheduler import SchedulerRunResponse, NotificationListResponse, NotificationOutboxResponse
from app.calendar.scheduler import SchedulerEngine

router = APIRouter()
scheduler_engine = SchedulerEngine()


@router.post("/scheduler/run", response_model=SchedulerRunResponse)
async def run_scheduler() -> SchedulerRunResponse:
    result = await scheduler_engine.run_due_reminders()
    return SchedulerRunResponse(**result)


@router.get("/scheduler/notifications", response_model=NotificationListResponse)
async def list_notifications(status: str | None = Query(None)) -> NotificationListResponse:
    if not scheduler_engine.enabled:
        return NotificationListResponse(notifications=[], total=0)
    result = await scheduler_engine.repository.list_notifications(status)
    return NotificationListResponse(
        notifications=[NotificationOutboxResponse(**n) for n in result],
        total=len(result)
    )