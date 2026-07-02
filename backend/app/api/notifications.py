from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from app.schemas.notifications import (
    NotificationIngestRequest, NotificationIngestResponse,
    NotificationListResponse, NotificationResponse,
    AlertListResponse, ImportantAlertResponse
)
from app.notifications.engine import NotificationEngine

router = APIRouter()
notification_engine = NotificationEngine()


@router.post("/notifications/ingest", response_model=NotificationIngestResponse)
async def ingest_notification(data: NotificationIngestRequest) -> NotificationIngestResponse:
    result = await notification_engine.ingest_notification(data.model_dump())
    return NotificationIngestResponse(**result)


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(importance: str | None = Query(None)) -> NotificationListResponse:
    if not notification_engine.enabled:
        return NotificationListResponse(notifications=[], total=0)
    result = await notification_engine.list_notifications(importance)
    return NotificationListResponse(
        notifications=[NotificationResponse(**n) for n in result],
        total=len(result)
    )


@router.get("/notifications/alerts", response_model=AlertListResponse)
async def list_alerts() -> AlertListResponse:
    if not notification_engine.enabled:
        return AlertListResponse(alerts=[], total=0)
    result = await notification_engine.list_important_alerts()
    return AlertListResponse(
        alerts=[ImportantAlertResponse(**a) for a in result],
        total=len(result)
    )


@router.post("/notifications/alerts/{alert_id}/ack", response_model=ImportantAlertResponse)
async def acknowledge_alert(alert_id: str) -> ImportantAlertResponse:
    if not notification_engine.enabled:
        raise HTTPException(status_code=503, detail="Notifications not enabled")
    result = await notification_engine.acknowledge_alert(alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return ImportantAlertResponse(**result)