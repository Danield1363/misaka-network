import pytest
from fastapi.testclient import TestClient
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_overview_returns_200(client):
    response = client.get("/api/overview")
    assert response.status_code == 200


def test_overview_has_required_fields(client):
    response = client.get("/api/overview")
    data = response.json()
    assert data["assistant"] == "Misaka"
    assert data["status"] == "online"
    assert "version" in data
    assert "llm_provider" in data
    assert "llm_model" in data
    assert "llm_primary_model" in data
    assert "llm_fallback_active" in data
    assert "gemini_configured" in data
    assert "memory_enabled" in data
    assert "tasks_enabled" in data or "tools_enabled" in data
    assert "calendar_enabled" in data
    assert "notifications_enabled" in data
    assert "desktop_enabled" in data
    assert "android_bridge_enabled" in data
    assert "voice_enabled" in data
    assert "pending_alerts" in data
    assert "critical_alerts" in data
    assert "pending_approvals" in data
    assert "last_error" in data
