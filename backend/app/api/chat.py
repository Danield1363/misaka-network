from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.brain.engine import BrainEngine

router = APIRouter()
brain = BrainEngine()


@router.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest) -> ChatResponse:
    return await brain.process_message(
        message=data.message,
        conversation_id=data.conversation_id,
        metadata=data.metadata
    )