import pytest
from fastapi.testclient import TestClient
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_get_settings_returns_200(client):
    response = client.get("/api/settings")
    assert response.status_code == 200


def test_get_settings_has_defaults(client):
    response = client.get("/api/settings")
    data = response.json()
    assert "voice_enabled" in data
    assert "auto_speak" in data
    assert "hud_enabled" in data
    assert data["voice_enabled"] is True
    assert data["auto_speak"] is False
    assert data["hud_enabled"] is False


def test_update_settings(client):
    response = client.put("/api/settings", json={
        "settings": {"auto_speak": True, "voice_rate": 1.2}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["updated"]["auto_speak"] is True
    assert data["updated"]["voice_rate"] == 1.2


def test_update_settings_ignores_unknown(client):
    response = client.put("/api/settings", json={
        "settings": {"unknown_key": "value"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


def test_reset_settings(client):
    client.put("/api/settings", json={"settings": {"auto_speak": True}})
    response = client.post("/api/settings/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["auto_speak"] is False
