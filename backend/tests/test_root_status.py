import pytest
from fastapi.testclient import TestClient
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_root_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_root_returns_assistant(client):
    response = client.get("/")
    data = response.json()
    assert data["assistant"] == "Misaka"


def test_root_returns_status_online(client):
    response = client.get("/")
    data = response.json()
    assert data["status"] == "online"


def test_root_returns_version(client):
    response = client.get("/")
    data = response.json()
    assert "version" in data


def test_root_returns_links(client):
    response = client.get("/")
    data = response.json()
    assert data["docs"] == "/docs"
    assert data["health"] == "/api/health"
    assert data["status_url"] == "/api/status"


def test_status_returns_200(client):
    response = client.get("/api/status")
    assert response.status_code == 200


def test_status_returns_assistant(client):
    response = client.get("/api/status")
    data = response.json()
    assert data["assistant"] == "Misaka"


def test_status_returns_version(client):
    response = client.get("/api/status")
    data = response.json()
    assert "version" in data


def test_status_returns_llm_provider(client):
    response = client.get("/api/status")
    data = response.json()
    assert "llm_provider" in data


def test_status_returns_memory_enabled(client):
    response = client.get("/api/status")
    data = response.json()
    assert "memory_enabled" in data


def test_status_returns_calendar_enabled(client):
    response = client.get("/api/status")
    data = response.json()
    assert "calendar_enabled" in data


def test_status_returns_tools_enabled(client):
    response = client.get("/api/status")
    data = response.json()
    assert data["tools_enabled"] is True


def test_status_no_secrets(client):
    response = client.get("/api/status")
    data = response.json()
    assert "GEMINI_API_KEY" not in str(data)
    assert "SUPABASE_SERVICE_ROLE_KEY" not in str(data)