import uuid

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status

from app.connection_manager import manager
from app.rooms import create_room, get_room, remove_user_from_room

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

@app.delete("/rooms/{room_id}/participants/{user_id}")
def api_remove_user_from_room(room_id: str, user_id: str):
    """Endpoint to remove a participant from a room."""
    room = get_room(room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id '{room_id}' not found."
        )
    if user_id not in room["participants"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found in room '{room_id}'."
        )
    
    remove_user_from_room(room_id, user_id)
    return {"message": f"User with id '{user_id}' removed from room '{room_id}'."}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """
    WebSocket endpoint for real-time communication in a room.
    Accepts connections, manages active participants, and handles disconnections.
    """
    connected = await manager.connect(room_id, websocket)
    if not connected:
        return  # Connection was rejected (room full)   

    try:
        while True:
            # Wait for a message from the client
            data = await websocket.receive_text()
            # Broadcast the received message to all participants in the room
            for connection in manager.active_connections.get(room_id, []):
                if connection != websocket:  # Don't send back to the sender
                    await connection.send_text(data)
    except WebSocketDisconnect:
        # Handle disconnection: remove the websocket from the room
        manager.disconnect(room_id, websocket)