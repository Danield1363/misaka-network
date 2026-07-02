import pytest
from fastapi.testclient import TestClient
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_health_returns_200(client):
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_returns_ok_status(client):
    response = client.get("/api/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_returns_assistant_name(client):
    response = client.get("/api/health")
    data = response.json()
    assert data["assistant"] == "Misaka"


def test_health_returns_version(client):
    response = client.get("/api/health")
    data = response.json()
    assert "version" in data