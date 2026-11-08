import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rooms import rooms

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

def test_join_non_existent_room():
    room_id = 'non-existent-id'
    response = client.post(f"/rooms/{room_id}/join")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": f"Room with id '{room_id}' not found."}

def test_join_full_room():
    response = client.post("/rooms")
    room_id = response.json()["id"]

    # Join the room with two participants
    client.post(f"/rooms/{room_id}/join")
    client.post(f"/rooms/{room_id}/join")

    # Attempt to join the full room
    response = client.post(f"/rooms/{room_id}/join")
    assert response.status_code == 409
    data = response.json()
    assert data == {"detail": f"Room with id '{room_id}' is full."}
    assert len(rooms[room_id]["participants"]) == 2


def test_join_room():
    response = client.post("/rooms")
    room_id = response.json()["id"]

    response = client.post(f"/rooms/{room_id}/join")
    data = response.json()

    assert response.status_code == 200

    assert len(rooms[room_id]["participants"]) == 1
    assert "participant_id" in data
    assert data["participant_id"] in rooms[room_id]["participants"]
    assert data["message"] == f"Room with id '{room_id}' joined successfully."

    response = client.get(f"/rooms/{room_id}")
    data = response.json()

    assert len(data["participants"]) == 1
    assert data["participants"][0] == rooms[room_id]["participants"][0]
    assert data["id"] == room_id


def test_different_participants_ide():
    response = client.post("/rooms")
    room_id = response.json()["id"]

    response1 = client.post(f"/rooms/{room_id}/join")
    participant_id1 = response1.json()["participant_id"]

    response2 = client.post(f"/rooms/{room_id}/join")
    participant_id2 = response2.json()["participant_id"]

    assert participant_id1 != participant_id2

def test_remove_user_from_room():
    response = client.post("/rooms")
    room_id = response.json()["id"]

    # Join the room with a participant
    join_response = client.post(f"/rooms/{room_id}/join")
    participant_id = join_response.json()["participant_id"]

    remove_response = client.delete(f"/rooms/{room_id}/participants/{participant_id}")
    assert remove_response.status_code == 200
    data = remove_response.json()
    assert data == {"message": f"User with id '{participant_id}' removed from room '{room_id}'."}
    assert participant_id not in rooms[room_id]["participants"]
    assert len(rooms[room_id]["participants"]) == 0

def test_remove_non_existent_user_from_room():
    response = client.post("/rooms")
    room_id = response.json()["id"]

    # Attempt to remove a non-existent participant
    non_existent_user_id = "non-existent-user-id"
    remove_response = client.delete(f"/rooms/{room_id}/participants/{non_existent_user_id}")
    assert remove_response.status_code == 404
    data = remove_response.json()
    assert data == {"detail": f"User with id '{non_existent_user_id}' not found in room '{room_id}'."}

def test_remove_user_from_non_existent_room():
    non_existent_room_id = "non-existent-room-id"
    user_id = "some-user-id"

    remove_response = client.delete(f"/rooms/{non_existent_room_id}/participants/{user_id}")
    assert remove_response.status_code == 404
    data = remove_response.json()
    assert data == {"detail": f"Room with id '{non_existent_room_id}' not found."}
    
    

    


    
    
    