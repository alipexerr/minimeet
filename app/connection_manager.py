from fastapi import WebSocket


class ConnectionManager:
    """
    Manages active WebSocket connections grouped by room.
    Tracks connected peers and enforces a maximum of two participants per room.
    """

    def __init__(self) -> None:
        # Maps room_id (str) -> list of active WebSocket objects
        self.active_connections: dict[str, list[WebSocket]] = {}
    """
    Why async? WebSocket operations (accept() and close())
    involve network I/O across the socket, so they must be awaited.
    """
    async def connect(self, room_id: str, websocket: WebSocket) -> bool:
        """
        Accepts the WebSocket connection and registers it in the specified room.
        If the room already has 2 participants, rejects the connection.
        Returns True if connected successfully, False otherwise.
        """
        connections = self.active_connections.setdefault(room_id, [])

        if len(connections) >= 2:
            # Room is full: close the connection with policy violation / custom code
            await websocket.close(code=4001, reason="Room is full")
            return False

        # Accept the handshake and add the socket to the room
        await websocket.accept()
        connections.append(websocket)
        return True

    def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        """
        Removes a WebSocket connection from the room.
        Safely handles non-existent rooms or connections.
        Cleans up the room entry if no connections remain.
        """
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)

            # If the room is now empty, delete its key to avoid memory leaks
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]


# Shared manager instance for the entire application
manager = ConnectionManager()

