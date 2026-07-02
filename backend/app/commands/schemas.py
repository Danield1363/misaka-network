from pydantic import BaseModel


class CommandRouteRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    context: dict | None = None


class CommandRouteResponse(BaseModel):
    type: str
    intent: str | None = None
    tool_name: str | None = None
    success: bool | None = None
    data: dict | None = None
    response_message: str | None = None
    message: str | None = None
    error: str | None = None
    metadata: dict | None = None


class ConfirmationRequest(BaseModel):
    confirmation_id: str


class ConfirmationResponse(BaseModel):
    id: str
    intent: str
    tool_name: str
    status: str
    message: str | None = None
