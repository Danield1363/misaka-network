from fastapi import APIRouter
from app.core.config import get_settings
from app.memory.engine import MemoryEngine
from app.calendar.engine import CalendarEngine
from app.notifications.engine import NotificationEngine

router = APIRouter()


@router.get("/status")
async def status() -> dict[str, str | bool]:
    settings = get_settings()
    memory_engine = MemoryEngine()
    calendar_engine = CalendarEngine()
    notification_engine = NotificationEngine()
    return {
        "assistant": "Misaka",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.GEMINI_MODEL if settings.LLM_PROVIDER == "gemini" else "mock",
        "memory_enabled": memory_engine.enabled,
        "calendar_enabled": calendar_engine.enabled,
        "notifications_enabled": notification_engine.enabled,
        "tools_enabled": True,
        "status": "online"
    }