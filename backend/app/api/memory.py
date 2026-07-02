from fastapi import APIRouter, HTTPException
from app.schemas.memory import MemoryCreate, MemoryResponse, MemorySearchRequest, MemorySearchResponse
from app.memory.engine import MemoryEngine

router = APIRouter()
memory_engine = MemoryEngine()


@router.post("/memory", response_model=MemoryResponse)
async def create_memory(data: MemoryCreate) -> MemoryResponse:
    if not memory_engine.enabled:
        raise HTTPException(status_code=503, detail="Memory not enabled")
    
    result = await memory_engine.create_memory(data.model_dump())
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create memory")
    
    return MemoryResponse(**result)


@router.get("/memory", response_model=list[MemoryResponse])
async def list_memories() -> list[MemoryResponse]:
    if not memory_engine.enabled:
        return []
    
    result = await memory_engine.repository.list()
    return [MemoryResponse(**m) for m in result]


@router.post("/memory/search", response_model=MemorySearchResponse)
async def search_memories(data: MemorySearchRequest) -> MemorySearchResponse:
    if not memory_engine.enabled:
        return MemorySearchResponse(results=[], total=0)
    
    results = await memory_engine.search_memories(data.query)
    return MemorySearchResponse(
        results=[MemoryResponse(**m) for m in results],
        total=len(results)
    )


@router.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str) -> dict[str, str]:
    if not memory_engine.enabled:
        raise HTTPException(status_code=503, detail="Memory not enabled")
    
    success = await memory_engine.repository.delete(memory_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {"status": "deleted"}