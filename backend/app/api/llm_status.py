from fastapi import APIRouter
from app.llm.gateway import LLMGateway

router = APIRouter()


@router.get("/llm/status")
async def llm_status() -> dict[str, str | bool | int | dict]:
    gateway = LLMGateway()
    return gateway.get_llm_status()
