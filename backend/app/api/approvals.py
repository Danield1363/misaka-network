from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any
from app.approvals.engine import ApprovalEngine

router = APIRouter()
approval_engine = ApprovalEngine()


class ApprovalRequest(BaseModel):
    action_name: str = Field(..., description="Action name")
    payload: dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "medium"
    description: str = ""


class ApprovalResponse(BaseModel):
    id: str | None = None
    status: str
    action_name: str
    risk_level: str
    description: str = ""


@router.get("/actions/pending-approvals")
async def pending_approvals() -> dict[str, Any]:
    approvals = await approval_engine.get_pending_approvals()
    return {"approvals": approvals, "total": len(approvals)}


@router.post("/actions/approvals", response_model=ApprovalResponse)
async def create_approval(data: ApprovalRequest) -> ApprovalResponse:
    result = await approval_engine.create_approval(data.model_dump())
    return ApprovalResponse(
        id=result.get("id"),
        status=result.get("status", "pending"),
        action_name=data.action_name,
        risk_level=data.risk_level,
        description=data.description,
    )


@router.post("/actions/approvals/{approval_id}/approve")
async def approve_action(approval_id: str) -> dict[str, str]:
    result = await approval_engine.approve(approval_id)
    if not result:
        raise HTTPException(status_code=404, detail="Approval not found")
    return {"status": "approved", "approval_id": approval_id}


@router.post("/actions/approvals/{approval_id}/deny")
async def deny_action(approval_id: str) -> dict[str, str]:
    result = await approval_engine.deny(approval_id)
    if not result:
        raise HTTPException(status_code=404, detail="Approval not found")
    return {"status": "denied", "approval_id": approval_id}
