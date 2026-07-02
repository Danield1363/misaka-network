import pytest
from unittest.mock import AsyncMock, patch
from app.notifications.engine import NotificationEngine


@pytest.fixture
def engine_enabled():
    with patch("app.notifications.engine.is_notifications_enabled", return_value=True):
        engine = NotificationEngine()
        engine.repository = AsyncMock()
        yield engine


@pytest.mark.asyncio
async def test_ack_all_alerts(engine_enabled):
    engine_enabled.repository.list_alerts.return_value = [
        {"id": "a1", "status": "pending"},
        {"id": "a2", "status": "pending"},
        {"id": "a3", "status": "pending"},
    ]
    engine_enabled.repository.acknowledge_alert.return_value = {"status": "acknowledged"}

    count = await engine_enabled.acknowledge_all_alerts()
    assert count == 3
    assert engine_enabled.repository.acknowledge_alert.call_count == 3


@pytest.mark.asyncio
async def test_ack_all_no_pending(engine_enabled):
    engine_enabled.repository.list_alerts.return_value = []
    count = await engine_enabled.acknowledge_all_alerts()
    assert count == 0


@pytest.mark.asyncio
async def test_get_summary(engine_enabled):
    engine_enabled.repository.list_alerts.return_value = [
        {"priority": "critical"},
        {"priority": "critical"},
        {"priority": "important"},
        {"priority": "normal"},
    ]
    summary = await engine_enabled.get_summary()
    assert summary["total_pending"] == 4
    assert summary["critical"] == 2
    assert summary["important"] == 1


@pytest.mark.asyncio
async def test_get_summary_empty(engine_enabled):
    engine_enabled.repository.list_alerts.return_value = []
    summary = await engine_enabled.get_summary()
    assert summary["total_pending"] == 0
    assert summary["critical"] == 0
    assert summary["important"] == 0


def test_engine_disabled_ack_all():
    with patch("app.notifications.engine.is_notifications_enabled", return_value=False):
        engine = NotificationEngine()
        import asyncio
        count = asyncio.get_event_loop().run_until_complete(engine.acknowledge_all_alerts())
        assert count == 0


def test_engine_disabled_summary():
    with patch("app.notifications.engine.is_notifications_enabled", return_value=False):
        engine = NotificationEngine()
        import asyncio
        summary = asyncio.get_event_loop().run_until_complete(engine.get_summary())
        assert summary == {"total_pending": 0, "critical": 0, "important": 0}
