import pytest
from unittest.mock import patch, MagicMock
from app.android.engine import AndroidEngine


@pytest.fixture
def engine_disabled():
    with patch("app.android.engine.get_settings") as mock:
        settings = MagicMock()
        settings.ANDROID_BRIDGE_ENABLED = False
        settings.SUPABASE_URL = ""
        settings.SUPABASE_SERVICE_ROLE_KEY = ""
        mock.return_value = settings
        yield AndroidEngine()


@pytest.fixture
def engine_enabled_no_db():
    with patch("app.android.engine.get_settings") as mock:
        settings = MagicMock()
        settings.ANDROID_BRIDGE_ENABLED = True
        settings.SUPABASE_URL = ""
        settings.SUPABASE_SERVICE_ROLE_KEY = ""
        mock.return_value = settings
        yield AndroidEngine()


@pytest.mark.asyncio
async def test_enqueue_disabled(engine_disabled):
    result = await engine_disabled.enqueue_action({"action_type": "vibrate"})
    assert result["status"] == "error"
    assert "disabled" in result["error"].lower()


@pytest.mark.asyncio
async def test_enqueue_enabled_no_db(engine_enabled_no_db):
    result = await engine_enabled_no_db.enqueue_action({"action_type": "vibrate"})
    assert result["status"] == "error"
    assert "database" in result["error"].lower()


@pytest.mark.asyncio
async def test_list_pending_disabled(engine_disabled):
    result = await engine_disabled.list_pending_actions()
    assert result == []


@pytest.mark.asyncio
async def test_list_pending_enabled_no_db(engine_enabled_no_db):
    result = await engine_enabled_no_db.list_pending_actions()
    assert result == []


@pytest.mark.asyncio
async def test_status_disabled(engine_disabled):
    status = await engine_disabled.get_status()
    assert status["enabled"] is False
    assert "disabled" in status["reason"].lower()


@pytest.mark.asyncio
async def test_status_enabled_no_db(engine_enabled_no_db):
    status = await engine_enabled_no_db.get_status()
    assert status["enabled"] is True
    assert status["connected"] is False
    assert "database" in status["reason"].lower()
