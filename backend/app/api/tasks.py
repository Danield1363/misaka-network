from fastapi import APIRouter, HTTPException, Query
from app.schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.tasks.engine import TaskEngine

router = APIRouter()
task_engine = TaskEngine()


@router.post("/tasks", response_model=TaskResponse)
async def create_task(data: TaskCreate) -> TaskResponse:
    if not task_engine.enabled:
        raise HTTPException(status_code=503, detail="Tasks not enabled")
    
    result = await task_engine.create_task(data.model_dump())
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create task")
    
    return TaskResponse(**result)


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(status: str | None = Query(None)) -> TaskListResponse:
    if not task_engine.enabled:
        return TaskListResponse(tasks=[], total=0)
    
    result = await task_engine.list_tasks(status)
    return TaskListResponse(
        tasks=[TaskResponse(**t) for t in result],
        total=len(result)
    )


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, data: TaskUpdate) -> TaskResponse:
    if not task_engine.enabled:
        raise HTTPException(status_code=503, detail="Tasks not enabled")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await task_engine.update_task(task_id, update_data)
    
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**result)


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: str) -> TaskResponse:
    if not task_engine.enabled:
        raise HTTPException(status_code=503, detail="Tasks not enabled")
    
    result = await task_engine.complete_task(task_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**result)


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str) -> dict[str, str]:
    if not task_engine.enabled:
        raise HTTPException(status_code=503, detail="Tasks not enabled")
    
    success = await task_engine.delete_task(task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"status": "deleted"}