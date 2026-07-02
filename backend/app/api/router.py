from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.status import router as status_router
from app.api.overview import router as overview_router
from app.api.chat import router as chat_router
from app.api.memory import router as memory_router
from app.api.tasks import router as tasks_router
from app.api.calendar import router as calendar_router
from app.api.reminders import router as reminders_router
from app.api.scheduler import router as scheduler_router
from app.api.tools import router as tools_router
from app.api.actions import router as actions_router
from app.api.persona import router as persona_router
from app.api.ui_config import router as ui_config_router
from app.api.voice_config import router as voice_config_router
from app.api.notifications import router as notifications_router
from app.api.llm_status import router as llm_status_router
from app.api.notification_actions import router as notification_actions_router
from app.api.android import router as android_router
from app.api.approvals import router as approvals_router
from app.api.commands import router as commands_router
from app.api.settings import router as settings_router
from app.api.devices import router as devices_router

api_router = APIRouter()

# Health & Status
api_router.include_router(health_router)
api_router.include_router(status_router)
api_router.include_router(overview_router)

# Core
api_router.include_router(chat_router)
api_router.include_router(persona_router)
api_router.include_router(llm_status_router)

# Features
api_router.include_router(memory_router)
api_router.include_router(tasks_router)
api_router.include_router(calendar_router)
api_router.include_router(reminders_router)
api_router.include_router(scheduler_router)

# Tools & Actions
api_router.include_router(tools_router)
api_router.include_router(actions_router)
api_router.include_router(approvals_router)
api_router.include_router(commands_router)

# Notifications
api_router.include_router(notifications_router)
api_router.include_router(notification_actions_router)

# Config
api_router.include_router(ui_config_router)
api_router.include_router(voice_config_router)
api_router.include_router(settings_router)

# Devices
api_router.include_router(android_router)
api_router.include_router(devices_router)
