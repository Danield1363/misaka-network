from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AndroidActionEnqueueRequest(BaseModel):
    device_id: str = "default"
    action_type: str
    payload: dict = {}
    risk_level: str = "safe"
    requires_confirmation: bool = False


class AndroidActionResponse(BaseModel):
    id: str
    device_id: str
    action_type: str
    payload: dict
    status: str
    risk_level: str
    requires_confirmation: bool
    created_at: float
    completed_at: float | None = None
    error_message: str | None = None


_android_actions: list[dict] = []


@router.post("/android/actions/enqueue")
async def enqueue_action(data: AndroidActionEnqueueRequest) -> dict:
    import time
    import hashlib
    action_id = hashlib.md5(f"{time.time()}{data.action_type}".encode()).hexdigest()[:12]
    action = {
        "id": action_id,
        "device_id": data.device_id,
        "action_type": data.action_type,
        "payload": data.payload,
        "status": "pending",
        "risk_level": data.risk_level,
        "requires_confirmation": data.requires_confirmation,
        "created_at": time.time(),
        "completed_at": None,
        "error_message": None
    }
    _android_actions.append(action)
    return {"action_id": action_id, "status": "pending"}


@router.get("/android/actions/pending")
async def list_pending_actions(device_id: str | None = None) -> dict:
    pending = [a for a in _android_actions if a["status"] == "pending"]
    if device_id:
        pending = [a for a in pending if a["device_id"] == device_id]
    return {"actions": pending, "total": len(pending)}


@router.post("/android/actions/{action_id}/complete")
async def complete_action(action_id: str) -> dict:
    import time
    for action in _android_actions:
        if action["id"] == action_id:
            action["status"] = "completed"
            action["completed_at"] = time.time()
            return {"action_id": action_id, "status": "completed"}
    return {"error": "Action not found"}


@router.post("/android/actions/{action_id}/fail")
async def fail_action(action_id: str, error_message: str = "") -> dict:
    import time
    for action in _android_actions:
        if action["id"] == action_id:
            action["status"] = "failed"
            action["completed_at"] = time.time()
            action["error_message"] = error_message
            return {"action_id": action_id, "status": "failed"}
    return {"error": "Action not found"}


@router.get("/android/status")
async def android_status() -> dict:
    pending = len([a for a in _android_actions if a["status"] == "pending"])
    completed = len([a for a in _android_actions if a["status"] == "completed"])
    failed = len([a for a in _android_actions if a["status"] == "failed"])
    return {
        "connected": False,
        "device_id": None,
        "pending_actions": pending,
        "completed_actions": completed,
        "failed_actions": failed,
        "last_seen": None,
        "bridge_type": "macrodroid"
    }
