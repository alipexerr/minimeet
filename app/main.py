from fastapi import FastAPI, HTTPException, status
from app.rooms import create_room, get_room
import uuid

# Create the FastAPI application instance
app = FastAPI(title="MiniMeet")


@app.get("/")
def read_root():
    """Root endpoint welcoming the user."""
    return {"message": "Welcome to MiniMeet!"}


@app.get("/health")
def health_check():
    """Health check endpoint to verify the server is running."""
    return {"status": "ok"}


@app.post("/rooms", status_code=status.HTTP_201_CREATED)
def api_create_room():
    """Endpoint to create a new video call room."""
    new_room = create_room()
    return new_room



@app.post("/rooms/{room_id}/join")
def join_room(room_id: str):
    """Endpoint to join an existing room."""
    room = get_room(room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id '{room_id}' not found."
        )
    if len(room["participants"]) >= 2:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Room with id '{room_id}' is full."
        )
    
    # We can accept or generate a unique ID for this participant
    participant_id = str(uuid.uuid4())
    room["participants"].append(participant_id)

    return {
        "message": f"Room with id '{room_id}' joined successfully.",
        "participant_id": participant_id
    }


@app.get("/rooms/{room_id}")
def api_get_room(room_id: str):
    """Endpoint to retrieve room details or return 404 if not found."""
    room = get_room(room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id '{room_id}' not found."
        )
    return room
