import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.tools.executor import ToolExecutor
from app.tools.base import ToolBase
from typing import Any


class MockTool(ToolBase):
    name: str = "test.mock"
    description: str = "Test tool"
    category: str = "test"
    danger_level: str = "safe"

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"success": True, "data": {"result": "ok"}, "metadata": {}}


@pytest.fixture
def executor():
    with patch("app.actions.engine.is_memory_enabled", return_value=False):
        ex = ToolExecutor()
        ex.registry._tools["test.mock"] = MockTool()
        yield ex


@pytest.mark.asyncio
async def test_execute_tool(executor):
    result = await executor.execute("test.mock", {"key": "value"})
    assert result["success"] is True
    assert result["tool"] == "test.mock"


@pytest.mark.asyncio
async def test_execute_nonexistent_tool(executor):
    result = await executor.execute("nonexistent.tool", {})
    assert result["success"] is False
    assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_dry_run(executor):
    result = await executor.execute("test.mock", {}, dry_run=True)
    assert result["success"] is True
    assert result["dry_run"] is True
    assert result["would_execute"] is True