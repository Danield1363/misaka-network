from fastapi import APIRouter, Query
from app.schemas.actions import ActionLogResponse, ActionLogListResponse
from app.actions.engine import ActionEngine

router = APIRouter()
action_engine = ActionEngine()


@router.get("/actions/logs", response_model=ActionLogListResponse)
async def list_action_logs(status: str | None = Query(None)) -> ActionLogListResponse:
    logs = await action_engine.list_action_logs(status)
    return ActionLogListResponse(
        logs=[ActionLogResponse(**l) for l in logs],
        total=len(logs)
    )


@router.get("/actions/logs/{action_id}", response_model=ActionLogResponse)
async def get_action_log(action_id: str) -> ActionLogResponse:
    log = await action_engine.get_action_log(action_id)
    if not log:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Action log not found")
    return ActionLogResponse(**log)