import pytest
from unittest.mock import AsyncMock, patch
from app.notifications.engine import NotificationEngine


@pytest.fixture
def engine_disabled():
    with patch("app.notifications.engine.is_notifications_enabled", return_value=False):
        yield NotificationEngine()


@pytest.fixture
def engine_enabled():
    with patch("app.notifications.engine.is_notifications_enabled", return_value=True):
        engine = NotificationEngine()
        engine.repository = AsyncMock()
        yield engine


@pytest.mark.asyncio
async def test_ingest_notification_disabled(engine_disabled):
    result = await engine_disabled.ingest_notification({
        "app_name": "Test",
        "received_at": "2026-07-02T21:00:00Z"
    })
    assert "importance" in result


@pytest.mark.asyncio
async def test_list_notifications_disabled(engine_disabled):
    result = await engine_disabled.list_notifications()
    assert result == []


@pytest.mark.asyncio
async def test_list_alerts_disabled(engine_disabled):
    result = await engine_disabled.list_important_alerts()
    assert result == []


@pytest.mark.asyncio
async def test_ingest_creates_alert(engine_enabled):
    engine_enabled.repository.create.return_value = {"id": "n1"}
    engine_enabled.repository.create_alert.return_value = {"id": "a1"}
    result = await engine_enabled.ingest_notification({
        "app_name": "WhatsApp",
        "content": "Urgente",
        "received_at": "2026-07-02T21:00:00Z"
    })
    assert result["should_alert"] is True
    engine_enabled.repository.create_alert.assert_called_once()


@pytest.mark.asyncio
async def test_ingest_no_alert_for_normal(engine_enabled):
    engine_enabled.repository.create.return_value = {"id": "n1"}
    result = await engine_enabled.ingest_notification({
        "app_name": "Game Store",
        "content": "Promoção",
        "received_at": "2026-07-02T21:00:00Z"
    })
    assert result["should_alert"] is False


def test_engine_disabled(engine_disabled):
    assert engine_disabled.enabled is False


@pytest.mark.asyncio
async def test_ingest_returns_classification_on_db_error():
    with patch("app.notifications.engine.is_notifications_enabled", return_value=True):
        engine = NotificationEngine()
        engine.repository = AsyncMock()
        engine.repository.create.side_effect = Exception("Database connection failed")

        result = await engine.ingest_notification({
            "app_name": "WhatsApp",
            "content": "URGENTE ME RESPONDE AGORA",
            "received_at": "2026-07-02T21:00:00Z"
        })

        assert result["importance"] == "critical"
        assert result["should_alert"] is True
        assert result["persistence_failed"] is True
        assert "urgente" in result["summary"].lower() or "urgente" in result.get("summary", "").lower()


@pytest.mark.asyncio
async def test_ingest_alert_failure_does_not_crash():
    with patch("app.notifications.engine.is_notifications_enabled", return_value=True):
        engine = NotificationEngine()
        engine.repository = AsyncMock()
        engine.repository.create.return_value = {"id": "n1"}
        engine.repository.create_alert.side_effect = Exception("Alert save failed")

        result = await engine.ingest_notification({
            "app_name": "WhatsApp",
            "content": "Emergência",
            "received_at": "2026-07-02T21:00:00Z"
        })

        assert result["importance"] == "critical"
        assert result["should_alert"] is True
        assert result["persistence_failed"] is True


@pytest.mark.asyncio
async def test_ingest_both_failures():
    with patch("app.notifications.engine.is_notifications_enabled", return_value=True):
        engine = NotificationEngine()
        engine.repository = AsyncMock()
        engine.repository.create.side_effect = Exception("DB down")
        engine.repository.create_alert.side_effect = Exception("Alert failed")

        result = await engine.ingest_notification({
            "app_name": "WhatsApp",
            "content": "Socorro",
            "received_at": "2026-07-02T21:00:00Z"
        })

        assert result["importance"] == "critical"
        assert result["should_alert"] is True
        assert result["persistence_failed"] is True