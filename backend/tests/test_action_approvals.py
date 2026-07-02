import pytest
from unittest.mock import AsyncMock, patch
from app.approvals.engine import ApprovalEngine


@pytest.fixture
def engine_enabled():
    with patch("app.approvals.engine.is_memory_enabled", return_value=True):
        engine = ApprovalEngine()
        engine.repository = AsyncMock()
        yield engine


@pytest.fixture
def engine_disabled():
    with patch("app.approvals.engine.is_memory_enabled", return_value=False):
        yield ApprovalEngine()


@pytest.mark.asyncio
async def test_create_approval(engine_enabled):
    engine_enabled.repository.create.return_value = {"id": "ap1", "status": "pending"}
    result = await engine_enabled.create_approval({
        "action_name": "open_app",
        "risk_level": "medium",
    })
    assert result["status"] == "pending"
    assert result["id"] == "ap1"


@pytest.mark.asyncio
async def test_create_disabled(engine_disabled):
    result = await engine_disabled.create_approval({"action_name": "test"})
    assert result["status"] == "pending"
    assert result["id"] == "local"


@pytest.mark.asyncio
async def test_get_pending(engine_enabled):
    engine_enabled.repository.list_pending.return_value = [{"id": "ap1"}]
    approvals = await engine_enabled.get_pending_approvals()
    assert len(approvals) == 1


@pytest.mark.asyncio
async def test_approve(engine_enabled):
    engine_enabled.repository.approve.return_value = {"id": "ap1", "status": "approved"}
    result = await engine_enabled.approve("ap1")
    assert result["status"] == "approved"


@pytest.mark.asyncio
async def test_deny(engine_enabled):
    engine_enabled.repository.deny.return_value = {"id": "ap1", "status": "denied"}
    result = await engine_enabled.deny("ap1")
    assert result["status"] == "denied"
