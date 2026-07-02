import pytest
from fastapi.testclient import TestClient
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_commands_route_returns_200(client):
    response = client.post("/api/commands/route", json={"message": "limpe os alertas atuais"})
    assert response.status_code == 200


def test_commands_route_clear_alerts(client):
    response = client.post("/api/commands/route", json={"message": "limpe os alertas atuais"})
    data = response.json()
    assert data["type"] == "command_executed"
    assert data["intent"] == "clear_alerts"


def test_commands_route_conversation(client):
    response = client.post("/api/commands/route", json={"message": "como vai você?"})
    data = response.json()
    assert data["type"] == "conversation"


def test_commands_route_hud_enable(client):
    response = client.post("/api/commands/route", json={"message": "ative o modo hud"})
    data = response.json()
    assert data["type"] == "command_executed"
    assert data["intent"] == "hud_on"


def test_commands_pending_confirmations(client):
    response = client.get("/api/commands/confirmations/pending")
    assert response.status_code == 200
    data = response.json()
    assert "confirmations" in data
    assert "total" in data
