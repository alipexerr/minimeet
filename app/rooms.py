import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# In-memory dictionary to store rooms.
# Key: room_id (str), Value: dict of room details
rooms: Dict[str, Dict[str, Any]] = {}


def create_room() -> Dict[str, Any]:
    """
    Creates a new room with a random UUID, records creation time,
    initializes an empty list of participants, and stores it in the dictionary.
    """
    room_id = str(uuid.uuid4())
    room = {
        "id": room_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "participants": []
    }
    rooms[room_id] = room
    return room


def get_room(room_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a room by its ID from the dictionary.
    Returns the room dictionary if found, or None if it doesn't exist.
    """
    return rooms.get(room_id)


def remove_user_from_room(room_id: str, user_id: str) -> bool:
    """
    Removes a participant from a room if both the room and user exist.
    Returns True if user was removed, False otherwise.
    """
    room = get_room(room_id)
    if room and user_id in room["participants"]:
        room["participants"].remove(user_id)
        return True
    return False

