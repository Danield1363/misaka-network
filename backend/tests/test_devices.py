import pytest
from fastapi.testclient import TestClient
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_list_devices_returns_200(client):
    response = client.get("/api/devices")
    assert response.status_code == 200


def test_list_devices_empty(client):
    response = client.get("/api/devices")
    data = response.json()
    assert data["total"] == 0
    assert data["devices"] == []


def test_register_device(client):
    response = client.post("/api/devices/register", json={
        "device_id": "test-device-1",
        "name": "Test Phone",
        "platform": "android",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "registered"
    assert data["device"]["device_id"] == "test-device-1"


def test_device_heartbeat(client):
    client.post("/api/devices/register", json={
        "device_id": "test-device-2",
        "name": "Test Phone",
        "platform": "android",
    })
    response = client.post("/api/devices/test-device-2/heartbeat")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_device_heartbeat_not_found(client):
    response = client.post("/api/devices/nonexistent/heartbeat")
    assert response.status_code == 404


def test_remove_device(client):
    client.post("/api/devices/register", json={
        "device_id": "test-device-3",
        "name": "Test Phone",
        "platform": "android",
    })
    response = client.delete("/api/devices/test-device-3")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "removed"


def test_remove_device_not_found(client):
    response = client.delete("/api/devices/nonexistent")
    assert response.status_code == 404


def test_register_and_list(client):
    # Clear any previous state by removing test devices
    for did in ["device-a", "device-b"]:
        client.delete(f"/api/devices/{did}")

    client.post("/api/devices/register", json={
        "device_id": "device-a",
        "name": "Phone A",
        "platform": "android",
    })
    client.post("/api/devices/register", json={
        "device_id": "device-b",
        "name": "Phone B",
        "platform": "ios",
    })
    response = client.get("/api/devices")
    data = response.json()
    assert data["total"] >= 2
    ids = [d["device_id"] for d in data["devices"]]
    assert "device-a" in ids
    assert "device-b" in ids
