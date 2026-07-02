from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter()


@router.get("/")
async def root() -> dict[str, str]:
    settings = get_settings()
    return {
        "assistant": "Misaka",
        "status": "online",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/health",
        "status_url": "/api/status"
    }