import logging
from fastapi import APIRouter
from app.core.config import get_settings
from app.memory.engine import MemoryEngine
from app.calendar.engine import CalendarEngine
from app.notifications.engine import NotificationEngine
from app.bridge.engine import notification_bridge
from app.android.engine import AndroidEngine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview")
async def overview() -> dict[str, str | bool | int | None]:
    settings = get_settings()
    memory_engine = MemoryEngine()
    calendar_engine = CalendarEngine()
    notification_engine = NotificationEngine()
    bridge_status = notification_bridge.get_status()
    android_engine = AndroidEngine()

    pending_alerts = 0
    critical_alerts = 0

    try:
        alerts = await notification_engine.list_important_alerts("pending")
        pending_alerts = len(alerts)
        critical_alerts = len([a for a in alerts if a.get("priority") == "critical"])
    except Exception as e:
        logger.error(f"Failed to count alerts: {e}")

    gemini_configured = bool(settings.GEMINI_API_KEY)
    llm_fallback_active = False
    llm_model = "mock"

    if settings.LLM_PROVIDER == "gemini":
        llm_model = settings.GEMINI_MODEL
        if gemini_configured:
            try:
                from app.llm.providers.gemini import GeminiProvider
                provider = GeminiProvider()
                status = provider.get_status()
                llm_model = status.get("active_model", settings.GEMINI_MODEL)
                llm_fallback_active = status.get("fallback_used", False)
            except Exception:
                pass

    return {
        "assistant": "Misaka",
        "status": "online",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": llm_model,
        "llm_primary_model": settings.GEMINI_MODEL,
        "llm_fallback_active": llm_fallback_active,
        "gemini_configured": gemini_configured,
        "memory_enabled": memory_engine.enabled,
        "calendar_enabled": calendar_engine.enabled,
        "notifications_enabled": notification_engine.enabled,
        "desktop_enabled": settings.DESKTOP_CONTROL_ENABLED,
        "android_bridge_enabled": settings.ANDROID_BRIDGE_ENABLED,
        "voice_enabled": True,
        "wake_word_available": settings.WAKE_WORD_ENABLED,
        "pending_alerts": pending_alerts,
        "critical_alerts": critical_alerts,
        "pending_approvals": 0,
        "tools_enabled": True,
        "last_error": None,
    }
