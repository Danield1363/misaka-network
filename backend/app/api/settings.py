from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any
from app.settings.engine import SettingsEngine

router = APIRouter()
settings_engine = SettingsEngine()


class SettingsUpdateRequest(BaseModel):
    settings: dict[str, Any] = Field(default_factory=dict)


@router.get("/settings")
async def get_settings() -> dict[str, Any]:
    return await settings_engine.get_settings()


@router.put("/settings")
async def update_settings(data: SettingsUpdateRequest) -> dict[str, Any]:
    updated = await settings_engine.update_settings(data.settings)
    return {"updated": updated, "total": len(updated)}


@router.post("/settings/reset")
async def reset_settings() -> dict[str, Any]:
    return await settings_engine.reset_settings()
