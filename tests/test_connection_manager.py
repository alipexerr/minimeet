from unittest.mock import AsyncMock, MagicMock

import pytest

from app.connection_manager import ConnectionManager

pytestmark = pytest.mark.asyncio

def test_connection_manager_initialization():
    manager = ConnectionManager()

    assert manager.active_connections == {}


async def test_connect_first_user():
    manager = ConnectionManager()
    websocket = MagicMock()
    mock_websocket = AsyncMock()
    websocket.accept = mock_websocket
    result = await manager.connect("room1", websocket)

    assert result is True
    assert "room1" in manager.active_connections
    assert manager.active_connections["room1"] == [websocket]
    websocket.accept.assert_awaited_once()


async def test_connect_second_user():
    manager = ConnectionManager()
    websocket1 = MagicMock()
    websocket2 = MagicMock()

    # Mock the accept method for both websockets
    websocket1.accept = AsyncMock()
    websocket2.accept = AsyncMock()

    # Connect the first user
    result1 = await manager.connect("room1", websocket1)
    assert result1 is True

    # Connect the second user
    result2 = await manager.connect("room1", websocket2)
    assert result2 is True

    assert "room1" in manager.active_connections
    assert manager.active_connections["room1"] == [websocket1, websocket2]
    websocket1.accept.assert_awaited_once()
    websocket2.accept.assert_awaited_once()

async def test_connect_third_user_rejected():
    manager = ConnectionManager()
    websocket1 = MagicMock()
    websocket2 = MagicMock()
    websocket3 = MagicMock()

    # Mock the accept and close methods for all websockets
    websocket1.accept = AsyncMock()
    websocket2.accept = AsyncMock()
    websocket3.close = AsyncMock()

    # Connect the first two users
    await manager.connect("room1", websocket1)
    await manager.connect("room1", websocket2)

    # Attempt to connect the third user
    result3 = await manager.connect("room1", websocket3)
    assert result3 is False

    assert "room1" in manager.active_connections
    assert manager.active_connections["room1"] == [websocket1, websocket2]
    assert len(manager.active_connections["room1"]) == 2
    assert websocket3 not in manager.active_connections["room1"]

    # Ensure the third user's connection was closed with the correct code and reason
    websocket3.close.assert_awaited_once_with(code=4001, reason="Room is full")


async def test_disconnect_user():
    manager = ConnectionManager()
    websocket1 = MagicMock()
    websocket2 = MagicMock()

    # Mock the accept method for both websockets
    websocket1.accept = AsyncMock()
    websocket2.accept = AsyncMock()

    # Connect two users
    await manager.connect("room1", websocket1)
    await manager.connect("room1", websocket2)

    # Disconnect the first user
    manager.disconnect("room1", websocket1)

    assert "room1" in manager.active_connections
    assert manager.active_connections["room1"] == [websocket2]

    # Disconnect the second user, which should remove the room entirely
    manager.disconnect("room1", websocket2)
    assert "room1" not in manager.active_connections

async def test_disconnect_nonexistent_user():
    manager = ConnectionManager()
    websocket1 = MagicMock()
    websocket2 = MagicMock()

    # Mock the accept method for both websockets
    websocket1.accept = AsyncMock()
    websocket2.accept = AsyncMock()

    # Connect one user
    await manager.connect("room1", websocket1)

    # Attempt to disconnect a user that was never connected
    manager.disconnect("room1", websocket2)

    # Ensure the original connection is still intact
    assert "room1" in manager.active_connections
    assert manager.active_connections["room1"] == [websocket1]

def test_disconnect_from_nonexistent_room():
    manager = ConnectionManager()
    websocket = MagicMock()

    # Attempt to disconnect from a room that doesn't exist
    manager.disconnect("nonexistent_room", websocket)

    # Ensure no rooms exist in the active connections
    assert manager.active_connections == {}

def test_disconnect_from_empty_room():
    manager = ConnectionManager()
    websocket = MagicMock()

    # Manually create an empty room
    manager.active_connections["empty_room"] = []

    # Attempt to disconnect from the empty room
    manager.disconnect("empty_room", websocket)

    # Ensure the empty room is removed from active connections
    assert "empty_room" not in manager.active_connections