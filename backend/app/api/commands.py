from fastapi import APIRouter, HTTPException
from app.commands.router import CommandRouter
from app.commands.schemas import CommandRouteRequest, CommandRouteResponse
from app.commands.confirmations import confirmation_manager
from app.tools.executor import ToolExecutor

router = APIRouter()
command_router = CommandRouter()
tool_executor = ToolExecutor()


@router.post("/commands/route", response_model=CommandRouteResponse)
async def route_command(data: CommandRouteRequest) -> CommandRouteResponse:
    result = await command_router.route(data.message, data.context)
    if result is None:
        return CommandRouteResponse(type="conversation")
    return CommandRouteResponse(**result)


@router.get("/commands/confirmations/pending")
async def pending_confirmations() -> dict:
    pending = confirmation_manager.get_pending()
    return {
        "confirmations": [
            {
                "id": c.id,
                "intent": c.intent,
                "tool_name": c.tool_name,
                "message": c.message,
                "parameters": c.parameters,
                "original_message": c.original_message,
                "created_at": c.created_at,
            }
            for c in pending
        ],
        "total": len(pending),
    }


@router.post("/commands/confirmations/{confirmation_id}/approve")
async def approve_confirmation(confirmation_id: str) -> dict:
    conf = confirmation_manager.approve(confirmation_id)
    if not conf:
        raise HTTPException(status_code=404, detail="Confirmation not found or already processed")

    try:
        result = await tool_executor.execute(
            tool_name=conf.tool_name,
            input_data=conf.parameters,
            context={},
            confirmed=True,
        )
        return {
            "id": conf.id,
            "status": "approved",
            "intent": conf.intent,
            "tool_name": conf.tool_name,
            "result": result,
        }
    except Exception as e:
        return {
            "id": conf.id,
            "status": "approved",
            "intent": conf.intent,
            "tool_name": conf.tool_name,
            "result": {"success": False, "error": str(e)},
        }


@router.post("/commands/confirmations/{confirmation_id}/deny")
async def deny_confirmation(confirmation_id: str) -> dict:
    conf = confirmation_manager.deny(confirmation_id)
    if not conf:
        raise HTTPException(status_code=404, detail="Confirmation not found or already processed")
    return {
        "id": conf.id,
        "status": "denied",
        "intent": conf.intent,
    }
