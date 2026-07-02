import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.calendar.scheduler import SchedulerEngine


@pytest.fixture
def engine_disabled():
    with patch("app.calendar.scheduler.is_memory_enabled", return_value=False):
        yield SchedulerEngine()


@pytest.fixture
def engine_enabled():
    with patch("app.calendar.scheduler.is_memory_enabled", return_value=True):
        engine = SchedulerEngine()
        engine.repository = MagicMock()
        engine.repository.get_due_reminders = AsyncMock(return_value=[])
        engine.repository.create_notification = AsyncMock(return_value={"id": "n1"})
        engine.repository.mark_reminder_triggered = AsyncMock(return_value={"id": "1"})
        yield engine


@pytest.mark.asyncio
async def test_run_disabled(engine_disabled):
    result = await engine_disabled.run_due_reminders()
    assert result["status"] == "disabled"
    assert result["processed_reminders"] == 0


@pytest.mark.asyncio
async def test_run_no_due_reminders(engine_enabled):
    result = await engine_enabled.run_due_reminders()
    assert result["status"] == "ok"
    assert result["processed_reminders"] == 0


@pytest.mark.asyncio
async def test_run_with_due_reminders(engine_enabled):
    engine_enabled.repository.get_due_reminders = AsyncMock(return_value=[
        {"id": "1", "title": "test", "remind_at": "2026-07-01T10:00:00Z"}
    ])
    result = await engine_enabled.run_due_reminders()
    assert result["processed_reminders"] == 1
    assert result["created_notifications"] == 1


@pytest.mark.asyncio
async def test_run_marks_triggered(engine_enabled):
    engine_enabled.repository.get_due_reminders = AsyncMock(return_value=[
        {"id": "1", "title": "test", "remind_at": "2026-07-01T10:00:00Z"}
    ])
    await engine_enabled.run_due_reminders()
    engine_enabled.repository.mark_reminder_triggered.assert_called_once_with("1")


def test_engine_has_enabled_flag(engine_disabled):
    assert engine_disabled.enabled is False