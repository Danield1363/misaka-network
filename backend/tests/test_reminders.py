import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.calendar.reminder_engine import ReminderEngine


@pytest.fixture
def engine_disabled():
    with patch("app.calendar.reminder_engine.is_memory_enabled", return_value=False):
        yield ReminderEngine()


@pytest.fixture
def engine_enabled():
    with patch("app.calendar.reminder_engine.is_memory_enabled", return_value=True):
        engine = ReminderEngine()
        engine.repository = MagicMock()
        engine.repository.create_reminder = AsyncMock(return_value={"id": "1", "title": "test"})
        engine.repository.list_reminders = AsyncMock(return_value=[{"id": "1", "title": "test"}])
        yield engine


@pytest.mark.asyncio
async def test_create_reminder_disabled(engine_disabled):
    result = await engine_disabled.create_reminder({"title": "test"})
    assert result == {}


@pytest.mark.asyncio
async def test_list_reminders_disabled(engine_disabled):
    result = await engine_disabled.list_reminders()
    assert result == []


@pytest.mark.asyncio
async def test_complete_reminder_disabled(engine_disabled):
    result = await engine_disabled.complete_reminder("1")
    assert result is None


@pytest.mark.asyncio
async def test_create_reminder_enabled(engine_enabled):
    result = await engine_enabled.create_reminder({"title": "test"})
    assert result["title"] == "test"


@pytest.mark.asyncio
async def test_list_reminders_enabled(engine_enabled):
    result = await engine_enabled.list_reminders()
    assert len(result) == 1


def test_engine_has_enabled_flag(engine_disabled):
    assert engine_disabled.enabled is False