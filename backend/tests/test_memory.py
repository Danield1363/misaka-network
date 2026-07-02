import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.memory.engine import MemoryEngine
from app.memory.repository import MemoryRepository
from app.memory.errors import MemoryError


@pytest.fixture
def mock_repository():
    with patch("app.memory.repository.get_supabase_client") as mock:
        repo = MemoryRepository()
        repo._client = MagicMock()
        yield repo


@pytest.fixture
def memory_engine_disabled():
    with patch("app.memory.engine.is_memory_enabled", return_value=False):
        engine = MemoryEngine()
        yield engine


@pytest.fixture
def memory_engine_enabled(mock_repository):
    with patch("app.memory.engine.is_memory_enabled", return_value=True):
        engine = MemoryEngine()
        engine.repository = mock_repository
        yield engine


@pytest.mark.asyncio
async def test_create_memory_disabled(memory_engine_disabled):
    result = await memory_engine_disabled.create_memory({"content": "test"})
    assert result == {}


@pytest.mark.asyncio
async def test_search_memories_disabled(memory_engine_disabled):
    result = await memory_engine_disabled.search_memories("test")
    assert result == []


@pytest.mark.asyncio
async def test_get_relevant_context_disabled(memory_engine_disabled):
    result = await memory_engine_disabled.get_relevant_context("test")
    assert result == []


@pytest.mark.asyncio
async def test_save_interaction_disabled(memory_engine_disabled):
    result = await memory_engine_disabled.save_interaction("conv-1", "hi", "hello", {})
    assert result == {}


@pytest.mark.asyncio
async def test_create_memory_enabled(memory_engine_enabled):
    memory_engine_enabled.repository.client.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[{"id": "1", "content": "test"}]
    )
    result = await memory_engine_enabled.create_memory({"content": "test"})
    assert result["content"] == "test"


@pytest.mark.asyncio
async def test_search_memories_enabled(memory_engine_enabled):
    memory_engine_enabled.repository.client.table.return_value.select.return_value.ilike.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{"id": "1", "content": "found"}]
    )
    result = await memory_engine_enabled.search_memories("test")
    assert len(result) == 1


def test_memory_engine_has_enabled_flag(memory_engine_disabled):
    assert memory_engine_disabled.enabled is False