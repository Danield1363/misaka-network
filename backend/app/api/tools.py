from fastapi import APIRouter
from app.schemas.tools import ToolListResponse, ToolInfo, ToolExecuteRequest, ToolExecuteResponse
from app.tools.registry import registry
from app.tools.executor import ToolExecutor

router = APIRouter()
tool_executor = ToolExecutor()


@router.get("/tools", response_model=ToolListResponse)
async def list_tools() -> ToolListResponse:
    tools = registry.list_tools()
    return ToolListResponse(tools=[ToolInfo(**t) for t in tools])


@router.post("/tools/execute", response_model=ToolExecuteResponse)
async def execute_tool(data: ToolExecuteRequest) -> ToolExecuteResponse:
    result = await tool_executor.execute(
        tool_name=data.tool_name,
        input_data=data.input_data,
        dry_run=data.dry_run,
        confirmed=data.confirmed
    )
    return ToolExecuteResponse(**result)