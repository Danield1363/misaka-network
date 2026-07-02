import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.coding.agent import CodingAgent


@pytest.fixture
def agent():
    yield CodingAgent()


@pytest.mark.asyncio
async def test_coding_agent_responds(agent):
    result = await agent.run("fastapi é legal", {})
    assert result["agent"] == "coding"
    assert "mock" in result["metadata"]
    assert result["metadata"]["mock"] is True


@pytest.mark.asyncio
async def test_coding_agent_metadata(agent):
    result = await agent.run("python", {})
    assert result["metadata"]["agent_type"] == "coding"