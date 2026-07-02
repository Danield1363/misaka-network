from fastapi import APIRouter
from app.core.config import get_settings
from app.memory.engine import MemoryEngine
from app.calendar.engine import CalendarEngine
from app.notifications.engine import NotificationEngine
from app.bridge.engine import notification_bridge

router = APIRouter()


@router.get("/overview")
async def overview() -> dict[str, str | bool | int]:
    settings = get_settings()
    memory_engine = MemoryEngine()
    calendar_engine = CalendarEngine()
    notification_engine = NotificationEngine()
    bridge_status = notification_bridge.get_status()

    return {
        "assistant": "Misaka",
        "status": "online",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.GEMINI_MODEL if settings.LLM_PROVIDER == "gemini" else "mock",
        "memory_enabled": memory_engine.enabled,
        "calendar_enabled": calendar_engine.enabled,
        "notifications_enabled": notification_engine.enabled,
        "desktop_enabled": True,
        "pending_alerts": bridge_status.get("notifications_today", 0),
        "critical_alerts": 0,
        "tools_enabled": True
    }