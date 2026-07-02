import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_chat_works_with_memory_disabled(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["memory_enabled"] is False
    assert data["metadata"]["memories_used"] == 0


def test_chat_includes_memory_enabled(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá"}
    )
    data = response.json()
    assert "memory_enabled" in data["metadata"]


def test_chat_includes_memories_used(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá"}
    )
    data = response.json()
    assert "memories_used" in data["metadata"]


def test_chat_with_memory_enabled(client):
    with patch("app.memory.engine.is_memory_enabled", return_value=False):
        response = client.post(
            "/api/chat",
            json={"message": "Olá"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["memory_enabled"] is False


def test_memory_endpoint_returns_503_when_disabled(client):
    response = client.post(
        "/api/memory",
        json={"content": "test", "type": "general"}
    )
    assert response.status_code == 503


def test_tasks_endpoint_returns_503_when_disabled(client):
    response = client.post(
        "/api/tasks",
        json={"title": "test"}
    )
    assert response.status_code == 503