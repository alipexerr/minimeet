from fastapi.testclient import TestClient

from app.connection_manager import manager
from app.main import app

client = TestClient(app)

def test_websocket_broadcast():
    with client.websocket_connect("/ws/test_room") as websocket1 , client.websocket_connect("/ws/test_room") as websocket2:   
            # Send a message from the first WebSocket
        websocket1.send_text("Hello, WebSocket!")
        
            # Receive the message on the second WebSocket
        response = websocket2.receive_text()
        assert response == "Hello, WebSocket!"


    assert "test_room" not in manager.active_connections

def test_websocket_disconnect():
    with client.websocket_connect("/ws/test_room") as websocket:
           # Send a message to ensure the connection is active
        websocket.send_text("Testing disconnect")
        response = websocket.receive_text()
        assert response == "Testing disconnect"
        
    