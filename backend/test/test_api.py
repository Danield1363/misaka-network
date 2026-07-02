import pytest
from fastapi.testclient import TestClient
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "misaka-core"


def test_chat_endpoint(client):
    response = client.post(
        "/api/chat",
        json={"message": "Olá Misaka"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["status"] == "success"