from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any
from app.devices.engine import DeviceEngine

router = APIRouter()
device_engine = DeviceEngine()


class DeviceRegisterRequest(BaseModel):
    device_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    platform: str = Field(default="unknown")
    metadata: dict[str, Any] = Field(default_factory=dict)


class HeartbeatRequest(BaseModel):
    device_id: str = Field(..., min_length=1)


@router.get("/devices")
async def list_devices() -> dict[str, Any]:
    devices = await device_engine.list_devices()
    return {"devices": devices, "total": len(devices)}


@router.post("/devices/register")
async def register_device(data: DeviceRegisterRequest) -> dict[str, Any]:
    device = await device_engine.register_device(
        device_id=data.device_id,
        name=data.name,
        platform=data.platform,
        metadata=data.metadata,
    )
    return {"device": device, "status": "registered"}


@router.post("/devices/{device_id}/heartbeat")
async def device_heartbeat(device_id: str) -> dict[str, str]:
    success = await device_engine.heartbeat(device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"status": "ok", "device_id": device_id}


@router.delete("/devices/{device_id}")
async def remove_device(device_id: str) -> dict[str, str]:
    success = await device_engine.remove_device(device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"status": "removed", "device_id": device_id}
