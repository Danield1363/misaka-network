from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse, CalendarEventListResponse
from app.calendar.engine import CalendarEngine

router = APIRouter()
calendar_engine = CalendarEngine()


@router.post("/calendar/events", response_model=CalendarEventResponse)
async def create_event(data: CalendarEventCreate) -> CalendarEventResponse:
    if not calendar_engine.enabled:
        raise HTTPException(status_code=503, detail="Calendar not enabled")
    result = await calendar_engine.create_event(data.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create event")
    return CalendarEventResponse(**result)


@router.get("/calendar/events", response_model=CalendarEventListResponse)
async def list_events(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None)
) -> CalendarEventListResponse:
    if not calendar_engine.enabled:
        return CalendarEventListResponse(events=[], total=0)
    result = await calendar_engine.list_events(from_date, to_date)
    return CalendarEventListResponse(
        events=[CalendarEventResponse(**e) for e in result],
        total=len(result)
    )


@router.patch("/calendar/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(event_id: str, data: CalendarEventUpdate) -> CalendarEventResponse:
    if not calendar_engine.enabled:
        raise HTTPException(status_code=503, detail="Calendar not enabled")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await calendar_engine.update_event(event_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return CalendarEventResponse(**result)


@router.post("/calendar/events/{event_id}/cancel", response_model=CalendarEventResponse)
async def cancel_event(event_id: str) -> CalendarEventResponse:
    if not calendar_engine.enabled:
        raise HTTPException(status_code=503, detail="Calendar not enabled")
    result = await calendar_engine.cancel_event(event_id)
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return CalendarEventResponse(**result)


@router.delete("/calendar/events/{event_id}")
async def delete_event(event_id: str) -> dict[str, str]:
    if not calendar_engine.enabled:
        raise HTTPException(status_code=503, detail="Calendar not enabled")
    success = await calendar_engine.repository.delete_event(event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"status": "deleted"}