from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app import create_app
from app.core.config import get_settings


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("VOICE_ENABLED", "true")
    monkeypatch.setenv("VOICE_PROVIDER", "mock")
    monkeypatch.setenv("VOICE_MOCK_TRANSCRIPT", "abrir youtube")
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()


def test_voice_status_mock(client):
    response = client.get("/api/voice/status")
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is True
    assert data["provider"] == "mock"
    assert data["mode"] == "cloud_voice"
    assert data["ready"] is True
    assert "webm" in data["accepted_formats"]


def test_voice_transcribe_mock(client):
    response = client.post(
        "/api/voice/transcribe",
        files={"audio": ("command.webm", BytesIO(b"fake-audio"), "audio/webm")},
        data={"language": "pt", "source": "test"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["text"] == "abrir youtube"
    assert data["provider"] == "mock"


def test_voice_transcribe_mock_empty_env_uses_dev_fallback(monkeypatch):
    monkeypatch.setenv("VOICE_ENABLED", "true")
    monkeypatch.setenv("VOICE_PROVIDER", "mock")
    monkeypatch.setenv("VOICE_MOCK_TRANSCRIPT", "")
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/voice/transcribe",
            files={"audio": ("command.webm", BytesIO(b"fake-audio"), "audio/webm")},
            data={"language": "pt", "source": "test"},
        )
    get_settings.cache_clear()

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["text"] == "abrir youtube"
    assert data["provider"] == "mock"


def test_voice_transcribe_without_file(client):
    response = client.post("/api/voice/transcribe", data={"language": "pt"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "audio_missing"
    assert data["safe_message"] == "Nenhum audio recebido."


def test_voice_transcribe_provider_unconfigured(monkeypatch):
    monkeypatch.setenv("VOICE_ENABLED", "true")
    monkeypatch.setenv("VOICE_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/voice/transcribe",
            files={"audio": ("command.webm", BytesIO(b"fake-audio"), "audio/webm")},
        )
    get_settings.cache_clear()

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "voice_provider_not_configured"
    assert data["safe_message"] == "Transcricao de voz nao configurada no backend."
