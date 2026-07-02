import pytest
from fastapi.testclient import TestClient
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_llm_status_returns_200(client):
    response = client.get("/api/llm/status")
    assert response.status_code == 200


def test_llm_status_has_required_fields(client):
    response = client.get("/api/llm/status")
    data = response.json()
    assert "provider" in data
    assert "ready" in data
