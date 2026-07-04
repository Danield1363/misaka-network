import pytest
from fastapi.testclient import TestClient
from app import create_app
from app.core.config import get_settings


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
    assert action["type"] == "open_url"
    assert action["provider"] == "google"
    assert action["query"] == "wake on lan"
    assert "google.com/search" in action["url"]
    assert "wake+on+lan" in action["url"]


def test_chat_search_youtube_returns_search_web_action(client):
    response = client.post("/api/chat", json={"message": "pesquisar alanzoka no YouTube"})
    assert response.status_code == 200
    data = response.json()
    action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert action["type"] == "open_url"
    assert action["provider"] == "youtube"
    assert action["query"] == "alanzoka"
    assert "youtube.com/results" in action["url"]
    assert "alanzoka" in action["url"]


def test_chat_open_youtube_channel_with_open_verb(client):
    response = client.post("/api/chat", json={"message": "abra o canal do alanzoka no youtube"})
    assert response.status_code == 200
    data = response.json()
    action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert action["type"] == "open_url"
    assert "youtube.com/results" in action["url"]
    assert "alanzoka" in action["url"]


@pytest.mark.parametrize(
    ("message", "app"),
    [
        ("abrir notepad", "notepad"),
        ("abrir explorer", "explorer"),
        ("abrir calculadora", "calculator"),
        ("abrir discord", "discord"),
        ("abrir vscode", "vscode"),
        ("abrir spotify", "spotify"),
    ],
)
def test_chat_desktop_apps_do_not_fall_to_llm(client, message, app):
    response = client.post("/api/chat", json={"message": message})
    assert response.status_code == 200
    data = response.json()
    action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert data["metadata"]["intent"] == "desktop"
    assert action["type"] == "open_app"
    assert action["app"] == app
    assert "tutorial" not in data["response"].lower()


def test_chat_voice_wake_phrase_youtube(client):
    response = client.post("/api/chat", json={"message": "Misaka, abra o YouTube"})
    assert response.status_code == 200
    data = response.json()
    action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert action["type"] == "open_url"
    assert action["url"] == "https://www.youtube.com"


def test_chat_open_youtube_video_search(client):
    response = client.post(
        "/api/chat",
        json={"message": "abrir video do alanzoka de minecraft"},
    )
    assert response.status_code == 200
    data = response.json()
    action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert "youtube.com/results" in action["url"]
    assert "alanzoka" in action["url"]
    assert "minecraft" in action["url"]


def test_chat_search_youtube_with_procurar(client):
    response = client.post(
        "/api/chat",
        json={"message": "procurar black wings no youtube"},
    )
    assert response.status_code == 200
    data = response.json()
    action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert action["type"] == "open_url"
    assert action["provider"] == "youtube"
    assert action["query"] == "black wings"
    assert "youtube.com/results" in action["url"]
    assert "black+wings" in action["url"]


@pytest.mark.parametrize(
    ("message", "provider", "needle"),
    [
        ("pesquise wake on lan no google", "google", "wake on lan"),
        ("pesquise misaka network no github", "github", "misaka network"),
        ("pesquise cobblemon no modrinth", "modrinth", "cobblemon"),
        ("procure atm 10 no curseforge", "curseforge", "atm 10"),
    ],
)
def test_chat_search_sites_do_not_fall_to_llm(client, message, provider, needle):
    response = client.post("/api/chat", json={"message": message})
    assert response.status_code == 200
    data = response.json()
    action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert action["type"] == "open_url"
    assert action["provider"] == provider
    assert needle.split()[0] in (action.get("query", "") + action.get("url", ""))


def test_chat_direct_commands_ignore_voice_mock_transcript(monkeypatch):
    monkeypatch.setenv("VOICE_PROVIDER", "mock")
    monkeypatch.setenv("VOICE_MOCK_TRANSCRIPT", "abrir youtube")
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as test_client:
        cases = [
            ("abrir youtube", "open_url", None, "youtube.com"),
            ("abrir notepad", "open_app", "notepad", None),
            ("abra explorer", "open_app", "explorer", None),
            ("abra calculadora", "open_app", "calculator", None),
            ("pesquise wake on lan no google", "open_url", None, "google.com/search"),
            (
                "abrir canal do alanzoka no youtube",
                "open_url",
                None,
                "youtube.com/results",
            ),
        ]

        for message, expected_type, expected_app, expected_url in cases:
            response = test_client.post("/api/chat", json={"message": message})
            assert response.status_code == 200
            data = response.json()
            action = data["metadata"]["client_action"]
            assert data["agent"] == "command_router"
            assert action["type"] == expected_type
            if expected_app:
                assert action["app"] == expected_app
            if expected_url:
                assert expected_url in action["url"]
            if "alanzoka" in message:
                assert "alanzoka" in action["url"]
            if "wake on lan" in message:
                assert action["query"] == "wake on lan"
    get_settings.cache_clear()


def test_chat_power_action_shutdown_returns_client_action(client):
    response = client.post("/api/chat", json={"message": "desligar computador"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "command_router"
    assert data["metadata"]["command"] == "power_action"
    action = data["metadata"]["client_action"]
    assert action["type"] == "power_action"
    assert action["action"] == "shutdown"


@pytest.mark.parametrize(
    ("message", "action"),
    [
        ("reiniciar computador", "restart"),
        ("bloquear computador", "lock"),
        ("suspender computador", "sleep"),
    ],
)
def test_chat_power_actions_return_client_action(client, message, action):
    response = client.post("/api/chat", json={"message": message})
    assert response.status_code == 200
    data = response.json()
    client_action = data["metadata"]["client_action"]
    assert data["agent"] == "command_router"
    assert client_action["type"] == "power_action"
    assert client_action["action"] == action
