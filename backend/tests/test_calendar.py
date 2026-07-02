import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.calendar.engine import CalendarEngine


@pytest.fixture
def engine_disabled():
    with patch("app.calendar.engine.is_memory_enabled", return_value=False):
        yield CalendarEngine()


@pytest.fixture
def engine_enabled():
    with patch("app.calendar.engine.is_memory_enabled", return_value=True):
        engine = CalendarEngine()
        engine.repository = MagicMock()
        engine.repository.create_event = AsyncMock(return_value={"id": "1", "title": "test"})
        engine.repository.list_events = AsyncMock(return_value=[{"id": "1", "title": "test"}])
        yield engine


@pytest.mark.asyncio
async def test_create_event_disabled(engine_disabled):
    result = await engine_disabled.create_event({"title": "test"})
    assert result == {}


@pytest.mark.asyncio
async def test_list_events_disabled(engine_disabled):
    result = await engine_disabled.list_events()
    assert result == []


@pytest.mark.asyncio
async def test_get_today_events_disabled(engine_disabled):
    result = await engine_disabled.get_today_events()
    assert result == []


@pytest.mark.asyncio
async def test_create_event_enabled(engine_enabled):
    result = await engine_enabled.create_event({"title": "test"})
    assert result["title"] == "test"


@pytest.mark.asyncio
async def test_list_events_enabled(engine_enabled):
    result = await engine_enabled.list_events()
    assert len(result) == 1


def test_engine_has_enabled_flag(engine_disabled):
    assert engine_disabled.enabled is False