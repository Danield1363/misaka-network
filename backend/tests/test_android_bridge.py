import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.android.engine import AndroidEngine


def _make_settings(bridge_enabled=True, db_configured=True):
    settings = MagicMock()
    settings.ANDROID_BRIDGE_ENABLED = bridge_enabled
    settings.SUPABASE_URL = "http://test.supabase.co" if db_configured else ""
    settings.SUPABASE_SERVICE_ROLE_KEY = "test-key" if db_configured else ""
    return settings


@pytest.fixture
def engine_enabled():
    with patch("app.android.engine.get_settings") as mock:
        mock.return_value = _make_settings(bridge_enabled=True, db_configured=True)
        engine = AndroidEngine()
        engine.repository = AsyncMock()
        yield engine


@pytest.fixture
def engine_disabled():
    with patch("app.android.engine.get_settings") as mock:
        mock.return_value = _make_settings(bridge_enabled=False)
        yield AndroidEngine()


@pytest.mark.asyncio
async def test_enqueue_action(engine_enabled):
    engine_enabled.repository.create.return_value = {"id": "act1", "status": "pending"}
    result = await engine_enabled.enqueue_action({
        "action_type": "vibrate",
        "payload": {"duration": 500},
        "risk_level": "safe",
    })
    assert result["status"] == "pending"
    assert result["id"] == "act1"


@pytest.mark.asyncio
async def test_enqueue_disabled(engine_disabled):
    result = await engine_disabled.enqueue_action({"action_type": "vibrate"})
    assert result["status"] == "error"
    assert "disabled" in result["error"].lower()


@pytest.mark.asyncio
async def test_list_pending(engine_enabled):
    engine_enabled.repository.list_pending.return_value = [
        {"id": "a1", "action_type": "vibrate"},
    ]
    actions = await engine_enabled.list_pending_actions()
    assert len(actions) == 1


@pytest.mark.asyncio
async def test_list_pending_disabled(engine_disabled):
    actions = await engine_disabled.list_pending_actions()
    assert actions == []


@pytest.mark.asyncio
async def test_complete_action(engine_enabled):
    engine_enabled.repository.complete.return_value = True
    result = await engine_enabled.complete_action("a1", {"success": True})
    assert result is True


@pytest.mark.asyncio
async def test_fail_action(engine_enabled):
    engine_enabled.repository.fail.return_value = True
    result = await engine_enabled.fail_action("a1", "timeout")
    assert result is True


@pytest.mark.asyncio
async def test_cancel_action(engine_enabled):
    engine_enabled.repository.cancel.return_value = True
    result = await engine_enabled.cancel_action("a1")
    assert result is True


@pytest.mark.asyncio
async def test_get_status_enabled(engine_enabled):
    engine_enabled.repository.list_pending.return_value = []
    status = await engine_enabled.get_status()
    assert status["enabled"] is True


@pytest.mark.asyncio
async def test_get_status_disabled(engine_disabled):
    status = await engine_disabled.get_status()
    assert status["enabled"] is False
    assert "disabled" in status["reason"].lower()
