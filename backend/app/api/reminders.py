from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from app.schemas.reminders import ReminderCreate, ReminderUpdate, ReminderResponse, ReminderListResponse
from app.calendar.reminder_engine import ReminderEngine

router = APIRouter()
reminder_engine = ReminderEngine()


@router.post("/reminders", response_model=ReminderResponse)
async def create_reminder(data: ReminderCreate) -> ReminderResponse:
    if not reminder_engine.enabled:
        raise HTTPException(status_code=503, detail="Reminders not enabled")
    result = await reminder_engine.create_reminder(data.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create reminder")
    return ReminderResponse(**result)


@router.get("/reminders", response_model=ReminderListResponse)
async def list_reminders(status: str | None = Query(None)) -> ReminderListResponse:
    if not reminder_engine.enabled:
        return ReminderListResponse(reminders=[], total=0)
    result = await reminder_engine.list_reminders(status)
    return ReminderListResponse(
        reminders=[ReminderResponse(**r) for r in result],
        total=len(result)
    )


@router.patch("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(reminder_id: str, data: ReminderUpdate) -> ReminderResponse:
    if not reminder_engine.enabled:
        raise HTTPException(status_code=503, detail="Reminders not enabled")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await reminder_engine.repository.update_reminder(reminder_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return ReminderResponse(**result)


@router.post("/reminders/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(reminder_id: str) -> ReminderResponse:
    if not reminder_engine.enabled:
        raise HTTPException(status_code=503, detail="Reminders not enabled")
    result = await reminder_engine.complete_reminder(reminder_id)
    if not result:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return ReminderResponse(**result)


@router.post("/reminders/{reminder_id}/cancel", response_model=ReminderResponse)
async def cancel_reminder(reminder_id: str) -> ReminderResponse:
    if not reminder_engine.enabled:
        raise HTTPException(status_code=503, detail="Reminders not enabled")
    result = await reminder_engine.cancel_reminder(reminder_id)
    if not result:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return ReminderResponse(**result)


@router.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str) -> dict[str, str]:
    if not reminder_engine.enabled:
        raise HTTPException(status_code=503, detail="Reminders not enabled")
    success = await reminder_engine.repository.delete_reminder(reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"status": "deleted"}