import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.tools.executor import ToolExecutor
from app.tools.base import ToolBase
from app.actions.engine import ActionEngine
from typing import Any


class MockTool(ToolBase):
    name: str = "test.mock"
    description: str = "Test tool"
    category: str = "test"
    danger_level: str = "safe"

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"success": True, "data": {"result": "ok"}, "metadata": {}}


class FailingTool(ToolBase):
    name: str = "test.fail"
    description: str = "Failing tool"
    category: str = "test"
    danger_level: str = "safe"

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        raise ValueError("Tool failed")


@pytest.fixture
def executor():
    with patch("app.actions.engine.is_memory_enabled", return_value=False):
        ex = ToolExecutor()
        ex.registry._tools["test.mock"] = MockTool()
        ex.registry._tools["test.fail"] = FailingTool()
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


@pytest.mark.asyncio
async def test_execute_failure(executor):
    result = await executor.execute("test.fail", {})
    assert result["success"] is False
    assert "Tool failed" in result["error"]


@pytest.mark.asyncio
async def test_action_log_created_on_success(executor):
    with patch.object(executor.action_engine, "log_action_start", new_callable=AsyncMock) as mock_start, \
         patch.object(executor.action_engine, "log_action_success", new_callable=AsyncMock) as mock_success:
        mock_start.return_value = {"id": "test-id", "status": "pending"}
        await executor.execute("test.mock", {})
        mock_start.assert_called_once()
        mock_success.assert_called_once()
        call_args = mock_success.call_args
        assert call_args.kwargs["action_id"] == "test-id"


@pytest.mark.asyncio
async def test_action_log_created_on_failure(executor):
    with patch.object(executor.action_engine, "log_action_start", new_callable=AsyncMock) as mock_start, \
         patch.object(executor.action_engine, "log_action_error", new_callable=AsyncMock) as mock_error:
        mock_start.return_value = {"id": "test-id", "status": "pending"}
        await executor.execute("test.fail", {})
        mock_start.assert_called_once()
        mock_error.assert_called_once()
        call_args = mock_error.call_args
        assert call_args.kwargs["action_id"] == "test-id"