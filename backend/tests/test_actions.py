import pytest
from unittest.mock import AsyncMock, patch
from app.actions.engine import ActionEngine


@pytest.fixture
def engine():
    with patch("app.actions.engine.is_memory_enabled", return_value=False):
        yield ActionEngine()


@pytest.mark.asyncio
async def test_log_action_start(engine):
    result = await engine.log_action_start("test.action")
    assert result["status"] == "pending"
    assert result["id"] == "local"


@pytest.mark.asyncio
async def test_log_action_success_local(engine):
    result = await engine.log_action_success("local", output={"key": "value"})
    assert result["status"] == "success"
    assert result["id"] == "local"


@pytest.mark.asyncio
async def test_log_action_error_local(engine):
    result = await engine.log_action_error("local", error="test error")
    assert result["status"] == "failed"
    assert result["id"] == "local"


@pytest.mark.asyncio
async def test_log_action_success_none_id(engine):
    result = await engine.log_action_success(None, output={"key": "value"})
    assert result["status"] == "success"
    assert result["id"] is None


@pytest.mark.asyncio
async def test_list_logs_disabled(engine):
    result = await engine.list_action_logs()
    assert result == []


def test_engine_disabled(engine):
    assert engine.enabled is False