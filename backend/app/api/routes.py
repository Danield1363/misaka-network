from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    status: str = "success"


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "misaka-core",
        "version": "0.1 Genesis"
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest) -> ChatResponse:
    return ChatResponse(
        reply=f"Misaka recebeu sua mensagem: {data.message}",
        status="success"
    )