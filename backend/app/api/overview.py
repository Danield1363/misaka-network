import logging
from fastapi import APIRouter
from app.core.config import get_settings
from app.memory.engine import MemoryEngine
from app.calendar.engine import CalendarEngine
from app.notifications.engine import NotificationEngine
from app.bridge.engine import notification_bridge

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview")
async def overview() -> dict[str, str | bool | int]:
    settings = get_settings()
    memory_engine = MemoryEngine()
    calendar_engine = CalendarEngine()
    notification_engine = NotificationEngine()
    bridge_status = notification_bridge.get_status()

    pending_alerts = 0
    critical_alerts = 0

    try:
        alerts = await notification_engine.list_important_alerts("pending")
        pending_alerts = len(alerts)
        critical_alerts = len([a for a in alerts if a.get("priority") == "critical"])
    except Exception as e:
        logger.error(f"Failed to count alerts: {e}")

    gemini_configured = bool(settings.GEMINI_API_KEY)

    return {
        "assistant": "Misaka",
        "status": "online",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.GEMINI_MODEL if settings.LLM_PROVIDER == "gemini" else "mock",
        "gemini_configured": gemini_configured,
        "memory_enabled": memory_engine.enabled,
        "calendar_enabled": calendar_engine.enabled,
        "notifications_enabled": notification_engine.enabled,
        "desktop_enabled": True,
        "pending_alerts": pending_alerts,
        "critical_alerts": critical_alerts,
        "tools_enabled": True
    }