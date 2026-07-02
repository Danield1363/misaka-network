import pytest
from unittest.mock import MagicMock, patch
from app.tasks.engine import TaskEngine
from app.tasks.repository import TaskRepository


@pytest.fixture
def mock_repository():
    with patch("app.tasks.repository.get_supabase_client") as mock:
        repo = TaskRepository()
        repo._client = MagicMock()
        yield repo


@pytest.fixture
def task_engine_disabled():
    with patch("app.tasks.engine.is_memory_enabled", return_value=False):
        engine = TaskEngine()
        yield engine


@pytest.fixture
def task_engine_enabled(mock_repository):
    with patch("app.tasks.engine.is_memory_enabled", return_value=True):
        engine = TaskEngine()
        engine.repository = mock_repository
        yield engine


@pytest.mark.asyncio
async def test_create_task_disabled(task_engine_disabled):
    result = await task_engine_disabled.create_task({"title": "test"})
    assert result == {}


@pytest.mark.asyncio
async def test_list_tasks_disabled(task_engine_disabled):
    result = await task_engine_disabled.list_tasks()
    assert result == []


@pytest.mark.asyncio
async def test_get_task_disabled(task_engine_disabled):
    result = await task_engine_disabled.get_task("1")
    assert result is None


@pytest.mark.asyncio
async def test_complete_task_disabled(task_engine_disabled):
    result = await task_engine_disabled.complete_task("1")
    assert result is None


@pytest.mark.asyncio
async def test_delete_task_disabled(task_engine_disabled):
    result = await task_engine_disabled.delete_task("1")
    assert result is False


@pytest.mark.asyncio
async def test_create_task_enabled(task_engine_enabled):
    task_engine_enabled.repository.client.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[{"id": "1", "title": "test", "status": "pending"}]
    )
    result = await task_engine_enabled.create_task({"title": "test"})
    assert result["title"] == "test"
    assert result["status"] == "pending"


@pytest.mark.asyncio
async def test_list_tasks_enabled(task_engine_enabled):
    task_engine_enabled.repository.client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{"id": "1", "title": "task1"}]
    )
    result = await task_engine_enabled.list_tasks()
    assert len(result) == 1


@pytest.mark.asyncio
async def test_complete_task_enabled(task_engine_enabled):
    task_engine_enabled.repository.client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"id": "1", "status": "done"}]
    )
    result = await task_engine_enabled.complete_task("1")
    assert result["status"] == "done"


def test_task_engine_has_enabled_flag(task_engine_disabled):
    assert task_engine_disabled.enabled is False