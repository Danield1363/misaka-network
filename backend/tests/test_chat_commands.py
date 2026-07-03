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
    assert data["agent"] != "command_router"


def test_chat_open_youtube_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "abra o youtube"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "command_router"
    assert data["metadata"]["intent"] == "web_action"
    assert data["metadata"]["command"] == "open_url"
    assert data["metadata"]["response_mode"] == "action_short"
    assert data["metadata"]["client_action"]["type"] == "open_url"
    assert data["metadata"]["client_action"]["url"] == "https://www.youtube.com"


def test_chat_open_discord_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "abra o discord"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "command_router"
    assert data["metadata"]["intent"] == "desktop"
    assert data["metadata"]["command"] == "open_app"
    assert data["metadata"]["response_mode"] == "action_short"
    assert data["metadata"]["client_action"]["type"] == "open_app"
    assert data["metadata"]["client_action"]["app"] == "discord"


def test_chat_abrir_discord_no_llm(client):
    response = client.post("/api/chat", json={"message": "abrir discord"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "command_router"
    assert data["metadata"]["intent"] == "desktop"
    assert data["metadata"]["client_action"]["app"] == "discord"
    assert "tutorial" not in data["response"].lower()
    assert len(data["response"]) < 200


def test_chat_open_vscode_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "abra o vs code"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "command_router"
    assert data["metadata"]["client_action"]["type"] == "open_app"
    assert data["metadata"]["client_action"]["app"] == "vscode"


def test_chat_search_youtube_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "canal do alanzoka"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "command_router"
    assert "client_action" in data["metadata"]
    assert data["metadata"]["client_action"]["type"] == "open_url"
    assert "alanzoka" in data["metadata"]["client_action"]["url"]


def test_chat_open_notepad_ptbr_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "abrir notepad no meu computador"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "command_router"
    assert data["metadata"]["intent"] == "desktop"
    assert data["metadata"]["command"] == "open_app"
    assert data["metadata"]["response_mode"] == "action_short"
    assert data["metadata"]["client_action"]["type"] == "open_app"
    assert data["metadata"]["client_action"]["app"] == "notepad"


def test_chat_open_explorer_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "abra explorer"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "command_router"
    assert data["metadata"]["client_action"]["type"] == "open_app"
    assert data["metadata"]["client_action"]["app"] == "explorer"


def test_chat_open_calculator_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "abrir calculadora"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "command_router"
    assert data["metadata"]["client_action"]["type"] == "open_app"
    assert data["metadata"]["client_action"]["app"] == "calculator"


def test_chat_search_google_returns_search_web_action(client):
    response = client.post("/api/chat", json={"message": "pesquisar wake on lan no Google"})
    assert response.status_code == 200
    data = response.json()
    action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert action["type"] == "search_web"
    assert action["provider"] == "google"
    assert action["query"] == "wake on lan"


def test_chat_search_youtube_returns_search_web_action(client):
    response = client.post("/api/chat", json={"message": "pesquisar alanzoka no YouTube"})
    assert response.status_code == 200
    data = response.json()
    action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert action["type"] == "search_web"
    assert action["provider"] == "youtube"
    assert action["query"] == "alanzoka"


def test_chat_open_youtube_channel_with_open_verb(client):
    response = client.post("/api/chat", json={"message": "abra o canal do alanzoka no youtube"})
    assert response.status_code == 200
    data = response.json()
    action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert action["type"] == "open_url"
    assert "youtube.com/results" in action["url"]
    assert "alanzoka" in action["url"]
