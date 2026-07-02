from pydantic import BaseModel, Field
from typing import Any


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Mensagem do usuário")
    conversation_id: str | None = Field(None, description="ID da conversa")
    metadata: dict[str, Any] | None = Field(None, description="Metadados extras")


class ChatResponse(BaseModel):
    response: str
    agent: str
    model: str | None = None
    execution_time: float
    conversation_id: str
    metadata: dict[str, Any]