import pytest
from app.tools.registry import ToolRegistry
from app.tools.base import ToolBase
from app.tools.errors import ToolNotFoundError
from typing import Any


class MockTool(ToolBase):
    name: str = "mock.tool"
    description: str = "Mock tool"
    category: str = "mock"
    danger_level: str = "safe"

    async def run(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"success": True, "data": {"input": input_data}, "metadata": {}}


def test_register_tool():
    reg = ToolRegistry()
    tool = MockTool()
    reg.register(tool)
    assert reg.has_tool("mock.tool")


def test_get_tool():
    reg = ToolRegistry()
    tool = MockTool()
    reg.register(tool)
    result = reg.get_tool("mock.tool")
    assert result.name == "mock.tool"


def test_list_tools():
    reg = ToolRegistry()
    tool = MockTool()
    reg.register(tool)
    tools = reg.list_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "mock.tool"


def test_tool_not_found():
    reg = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        reg.get_tool("nonexistent.tool")


def test_prevent_duplicate():
    reg = ToolRegistry()
    tool1 = MockTool()
    tool2 = MockTool()
    reg.register(tool1)
    reg.register(tool2)
    tools = reg.list_tools()
    assert len(tools) == 1