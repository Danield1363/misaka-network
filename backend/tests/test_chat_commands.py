import pytest
from fastapi.testclient import TestClient
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_chat_clear_alerts(client):
    response = client.post("/api/chat", json={"message": "limpe os alertas atuais"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] == "command"
    assert data["metadata"]["command"] == "clear_alerts"
    assert data["metadata"]["ui_effect"] == "refresh_alerts"
    assert data["agent"] == "command_router"


def test_chat_hud_enable(client):
    response = client.post("/api/chat", json={"message": "ative o modo hud"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] == "command"
    assert data["metadata"]["command"] == "hud_on"
    assert data["metadata"]["ui_effect"] == "enable_hud"


def test_chat_hud_disable(client):
    response = client.post("/api/chat", json={"message": "desative o modo hud"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] == "command"
    assert data["metadata"]["command"] == "hud_off"
    assert data["metadata"]["ui_effect"] == "disable_hud"


def test_chat_voice_enable(client):
    response = client.post("/api/chat", json={"message": "ligue a voz"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] == "command"
    assert data["metadata"]["command"] == "voice_on"
    assert data["metadata"]["ui_effect"] == "enable_voice"


def test_chat_voice_disable(client):
    response = client.post("/api/chat", json={"message": "desligue a voz"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] == "command"
    assert data["metadata"]["command"] == "voice_off"
    assert data["metadata"]["ui_effect"] == "disable_voice"


def test_chat_open_settings(client):
    response = client.post("/api/chat", json={"message": "abra configurações"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] == "command"
    assert data["metadata"]["command"] == "open_settings"
    assert data["metadata"]["ui_effect"] == "open_settings"


def test_chat_clear_chat(client):
    response = client.post("/api/chat", json={"message": "limpe o chat"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] == "command"
    assert data["metadata"]["command"] == "clear_chat"
    assert data["metadata"]["ui_effect"] == "clear_chat"


def test_chat_show_alerts(client):
    response = client.post("/api/chat", json={"message": "mostre os alertas"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] == "command"
    assert data["metadata"]["command"] == "show_alerts"
    assert data["metadata"]["ui_effect"] == "refresh_alerts"


def test_chat_conversation_not_command(client):
    response = client.post("/api/chat", json={"message": "como vai você?"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] != "command"
    assert "agent" in data


def test_chat_open_youtube_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "abra o youtube"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] == "command"
    assert "client_action" in data["metadata"]
    assert data["metadata"]["client_action"]["type"] in ("open_url", "open_app")
    assert "youtube" in str(data["metadata"]["client_action"])


def test_chat_open_discord_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "abra o discord"})
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["intent"] == "command"
    assert "client_action" in data["metadata"]
    assert data["metadata"]["client_action"]["type"] == "open_app"
    assert data["metadata"]["client_action"]["app"] == "discord"


def test_chat_open_vscode_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "abra o vs code"})
    assert response.status_code == 200
    data = response.json()
    assert "client_action" in data["metadata"]
    assert data["metadata"]["client_action"]["type"] == "open_app"
    assert data["metadata"]["client_action"]["app"] == "vscode"


def test_chat_search_youtube_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "canal do alanzoka"})
    assert response.status_code == 200
    data = response.json()
    assert "client_action" in data["metadata"]
    assert data["metadata"]["client_action"]["type"] == "open_url"
    assert "alanzoka" in data["metadata"]["client_action"]["url"]
