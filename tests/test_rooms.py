from app.main import app
from app.rooms import rooms
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_rooms():
    rooms.clear()
    yield
    rooms.clear()

def test_create_room():
    
    response = client.post("/rooms")

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "created_at" in data
    assert data["participants"] == []

    assert len(rooms) == 1
    assert rooms[data["id"]] == data


def test_get_room():
    response = client.post("/rooms")
    room_id = response.json()["id"]

    response = client.get(f"/rooms/{room_id}")
    data = response.json()

    assert response.status_code == 200
    assert data == rooms[room_id]
    assert data["id"] == room_id
    assert data["created_at"] is not None
    assert data["participants"] == []


def test_get_non_existent_room():
    room_id = 'non-existent-id'
    response = client.get(f"/rooms/{room_id}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": f"Room with id '{room_id}' not found."}
    
    