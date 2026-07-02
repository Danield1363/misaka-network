from fastapi import APIRouter, HTTPException
from app.notifications.engine import NotificationEngine
from app.schemas.notifications import ImportantAlertResponse

router = APIRouter()


@router.post("/notifications/alerts/ack-all")
async def acknowledge_all_alerts() -> dict[str, int | str]:
    engine = NotificationEngine()
    if not engine.enabled:
        raise HTTPException(status_code=503, detail="Notifications not enabled")

    alerts = await engine.list_important_alerts("pending")
    acked = 0
    for alert in alerts:
        alert_id = alert.get("id")
        if alert_id:
            result = await engine.acknowledge_alert(alert_id)
            if result:
                acked += 1

    return {
        "status": "ok",
        "acked_count": acked,
        "total_pending": len(alerts),
        "message": f"Marquei {acked} alertas como vistos.",
    }


@router.get("/notifications/summary")
async def notifications_summary() -> dict[str, int | str]:
    engine = NotificationEngine()
    if not engine.enabled:
        return {"total_pending": 0, "critical": 0, "important": 0}

    alerts = await engine.list_important_alerts("pending")
    critical = len([a for a in alerts if a.get("priority") == "critical"])
    important = len([a for a in alerts if a.get("priority") == "important"])

    return {
        "total_pending": len(alerts),
        "critical": critical,
        "important": important,
    }
