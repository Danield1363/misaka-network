import pytest
from unittest.mock import MagicMock, patch
from app.agents.calendar.agent import CalendarAgent


@pytest.fixture
def agent():
    with patch("app.calendar.engine.is_memory_enabled", return_value=False):
        with patch("app.calendar.reminder_engine.is_memory_enabled", return_value=False):
            yield CalendarAgent()


@pytest.mark.asyncio
async def test_reminder_keyword(agent):
    result = await agent.run("me lembra de estudar", {})
    assert "lembrete" in result["response"].lower() or "data" in result["response"].lower()
    assert result["agent"] == "calendar"


@pytest.mark.asyncio
async def test_calendar_keyword(agent):
    result = await agent.run("o que tenho na agenda?", {})
    assert result["agent"] == "calendar"


@pytest.mark.asyncio
async def test_fallback(agent):
    result = await agent.run("isso é ambíguo", {})
    assert "detalhes" in result["response"].lower() or "agenda" in result["response"].lower()


@pytest.mark.asyncio
async def test_agent_returns_metadata(agent):
    result = await agent.run("me lembra algo", {})
    assert "metadata" in result
    assert "intent" in result["metadata"]