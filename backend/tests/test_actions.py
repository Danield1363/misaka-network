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


@pytest.mark.asyncio
async def test_log_action_success(engine):
    result = await engine.log_action_success("test.action")
    assert result["status"] == "success"


@pytest.mark.asyncio
async def test_log_action_error(engine):
    result = await engine.log_action_error("test.action", error="test error")
    assert result["status"] == "failed"


@pytest.mark.asyncio
async def test_list_logs_disabled(engine):
    result = await engine.list_action_logs()
    assert result == []


def test_engine_disabled(engine):
    assert engine.enabled is False