from fastapi import APIRouter
from app.commands.router import CommandRouter
from app.commands.schemas import CommandRouteRequest, CommandRouteResponse
from app.commands.confirmations import confirmation_manager

router = APIRouter()
command_router = CommandRouter()


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
                "created_at": c.created_at
            }
            for c in pending
        ],
        "total": len(pending)
    }


@router.post("/commands/confirmations/{confirmation_id}/approve")
async def approve_confirmation(confirmation_id: str) -> dict:
    conf = confirmation_manager.approve(confirmation_id)
    if not conf:
        return {"error": "Confirmation not found"}
    from app.commands.router import CommandRouter
    router_instance = CommandRouter()
    result = await router_instance.route(conf.message, conf.parameters)
    return {
        "id": conf.id,
        "status": "approved",
        "result": result
    }


@router.post("/commands/confirmations/{confirmation_id}/deny")
async def deny_confirmation(confirmation_id: str) -> dict:
    conf = confirmation_manager.deny(confirmation_id)
    if not conf:
        return {"error": "Confirmation not found"}
    return {"id": conf.id, "status": "denied"}
