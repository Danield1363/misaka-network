from fastapi import APIRouter
from pydantic import BaseModel
import time
import uuid

router = APIRouter()


class ApprovalRequest(BaseModel):
    action_name: str
    payload: dict = {}
    risk_level: str = "medium"


_approvals: list[dict] = []


@router.get("/actions/pending-approvals")
async def pending_approvals() -> dict:
    pending = [a for a in _approvals if a["status"] == "pending"]
    return {"approvals": pending, "total": len(pending)}


@router.post("/actions/approvals")
async def create_approval(data: ApprovalRequest) -> dict:
    approval_id = str(uuid.uuid4())[:8]
    approval = {
        "id": approval_id,
        "action_name": data.action_name,
        "payload": data.payload,
        "risk_level": data.risk_level,
        "status": "pending",
        "created_at": time.time(),
        "approved_at": None,
        "denied_at": None
    }
    _approvals.append(approval)
    return {"id": approval_id, "status": "pending"}


@router.post("/actions/approvals/{approval_id}/approve")
async def approve_action(approval_id: str) -> dict:
    for approval in _approvals:
        if approval["id"] == approval_id:
            approval["status"] = "approved"
            approval["approved_at"] = time.time()
            return {"id": approval_id, "status": "approved"}
    return {"error": "Approval not found"}


@router.post("/actions/approvals/{approval_id}/deny")
async def deny_action(approval_id: str) -> dict:
    for approval in _approvals:
        if approval["id"] == approval_id:
            approval["status"] = "denied"
            approval["denied_at"] = time.time()
            return {"id": approval_id, "status": "denied"}
    return {"error": "Approval not found"}
