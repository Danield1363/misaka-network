import pytest
from fastapi.testclient import TestClient
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_chat_accepts_valid_message(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá Misaka"}
    )
    assert response.status_code == 200


def test_chat_returns_response(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá Misaka"}
    )
    data = response.json()
    assert "response" in data


def test_chat_returns_agent(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá Misaka"}
    )
    data = response.json()
    assert "agent" in data
    assert data["agent"] == "conversation"


def test_chat_returns_conversation_id(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá Misaka"}
    )
    data = response.json()
    assert "conversation_id" in data
    assert len(data["conversation_id"]) > 0


def test_chat_returns_execution_time(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá Misaka"}
    )
    data = response.json()
    assert "execution_time" in data
    assert isinstance(data["execution_time"], float)


def test_chat_returns_metadata(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá Misaka"}
    )
    data = response.json()
    assert "metadata" in data
    assert isinstance(data["metadata"], dict)


def test_chat_rejects_empty_message(client):
    response = client.post(
        "/api/chat",
        json={"message": ""}
    )
    assert response.status_code == 422


def test_chat_greeting_response(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá"}
    )
    data = response.json()
    assert "Misaka" in data["response"]
    assert "Brain Engine" in data["response"]


def test_chat_general_response(client):
    response = client.post(
        "/api/chat",
        json={"message": "Como vai?"}
    )
    data = response.json()
    assert "Recebi sua mensagem" in data["response"]