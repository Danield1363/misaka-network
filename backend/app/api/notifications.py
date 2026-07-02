from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query, Header
from app.schemas.notifications import (
    NotificationIngestRequest, NotificationIngestResponse,
    NotificationListResponse, NotificationResponse,
    AlertListResponse, ImportantAlertResponse
)
from app.notifications.engine import NotificationEngine
from app.bridge.engine import notification_bridge

router = APIRouter()
notification_engine = NotificationEngine()


@router.post("/notifications/ingest", response_model=NotificationIngestResponse)
async def ingest_notification(
    data: NotificationIngestRequest,
    x_misaka_token: str | None = Header(None)
) -> NotificationIngestResponse:
    if not notification_bridge.verify_token(x_misaka_token):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    result = await notification_bridge.ingest(data.model_dump())

    if result.get("status") == "rate_limited":
        raise HTTPException(
            status_code=429,
            detail={
                "error": result.get("error"),
                "retry_after": result.get("retry_after")
            }
        )

    if result.get("status") == "duplicate":
        return NotificationIngestResponse(
            importance="normal",
            should_alert=False,
            summary="Duplicate notification",
            category="general",
            is_sensitive=False
        )

    return NotificationIngestResponse(
        importance=result.get("importance", "normal"),
        should_alert=result.get("should_alert", False),
        summary=result.get("summary", "Notification received"),
        category=result.get("category", "general"),
        is_sensitive=result.get("is_sensitive", False),
        persistence_failed=result.get("persistence_failed", False)
    )


@router.get("/notifications/bridge/status")
async def bridge_status() -> dict[str, str | int | None | bool]:
    return notification_bridge.get_status()


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