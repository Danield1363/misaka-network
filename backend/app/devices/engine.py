import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class DeviceEngine:
    def __init__(self) -> None:
        self._devices: dict[str, dict[str, Any]] = {}

    async def register_device(self, device_id: str, name: str, platform: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        device = {
            "device_id": device_id,
            "name": name,
            "platform": platform,
            "status": "online",
            "last_heartbeat": time.time(),
            "metadata": metadata or {},
        }
        self._devices[device_id] = device
        logger.info(f"Device registered: {device_id} ({name})")
        return device

    async def heartbeat(self, device_id: str) -> bool:
        if device_id in self._devices:
            self._devices[device_id]["last_heartbeat"] = time.time()
            self._devices[device_id]["status"] = "online"
            return True
        return False

    async def list_devices(self) -> list[dict[str, Any]]:
        now = time.time()
        for device in self._devices.values():
            if now - device["last_heartbeat"] > 300:
                device["status"] = "offline"
        return list(self._devices.values())

    async def get_device(self, device_id: str) -> dict[str, Any] | None:
        return self._devices.get(device_id)

    async def remove_device(self, device_id: str) -> bool:
        if device_id in self._devices:
            del self._devices[device_id]
            return True
        return False
