from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.status import router as status_router
from app.api.chat import router as chat_router
from app.api.memory import router as memory_router
from app.api.tasks import router as tasks_router
from app.api.calendar import router as calendar_router
from app.api.reminders import router as reminders_router
from app.api.scheduler import router as scheduler_router
from app.api.tools import router as tools_router
from app.api.actions import router as actions_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(status_router)
api_router.include_router(chat_router)
api_router.include_router(memory_router)
api_router.include_router(tasks_router)
api_router.include_router(calendar_router)
api_router.include_router(reminders_router)
api_router.include_router(scheduler_router)
api_router.include_router(tools_router)
api_router.include_router(actions_router)