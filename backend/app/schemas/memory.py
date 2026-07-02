from pydantic import BaseModel, Field
from typing import Any


class MemoryCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Conteúdo da memória")
    type: str = Field("general", description="Tipo da memória")
    source: str = Field("manual", description="Origem da memória")
    importance: int = Field(3, ge=1, le=5, description="Importância (1-5)")
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryUpdate(BaseModel):
    content: str | None = Field(None, min_length=1)
    type: str | None = None
    source: str | None = None
    importance: int | None = Field(None, ge=1, le=5)
    metadata: dict[str, Any] | None = None


class MemoryResponse(BaseModel):
    id: str
    content: str
    type: str
    source: str
    importance: int
    metadata: dict[str, Any]
    created_at: str
    updated_at: str


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Busca por texto")


class MemorySearchResponse(BaseModel):
    results: list[MemoryResponse]
    total: int