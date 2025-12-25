import pytest
from uuid import uuid4
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_connect_adds_user_connection(manager, websocket):
    user_id = uuid4()

    await manager.connect(user_id=user_id, websocket=websocket)

    websocket.accept.assert_awaited_once()
    assert manager.is_user_online(user_id) is True


@pytest.mark.asyncio
async def test_disconnect_removes_user_connection(manager, websocket):
    user_id = uuid4()

    await manager.connect(user_id=user_id, websocket=websocket)
    manager.disconnect(user_id=user_id, websocket=websocket)

    assert manager.is_user_online(user_id) is False


def test_join_and_leave_room(manager):
    room_id = uuid4()
    user_id = uuid4()

    manager.join_room(room_id=room_id, user_id=user_id)

    assert user_id in manager.room_online_members(room_id)

    manager.leave_room(room_id=room_id, user_id=user_id)

    assert manager.room_online_members(room_id) == set()


@pytest.mark.asyncio
async def test_send_to_user_sends_message(manager, websocket):
    user_id = uuid4()
    message = {"type": "test"}

    await manager.connect(user_id=user_id, websocket=websocket)
    await manager.send_to_user(user_id=user_id, message=message)

    websocket.send_json.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_broadcast_to_room(manager):
    room_id = uuid4()
    user1 = uuid4()
    user2 = uuid4()

    ws1 = AsyncMock()
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()

    ws2 = AsyncMock()
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()

    await manager.connect(user_id=user1, websocket=ws1)
    await manager.connect(user_id=user2, websocket=ws2)

    manager.join_room(room_id=room_id, user_id=user1)
    manager.join_room(room_id=room_id, user_id=user2)

    message = {"type": "broadcast"}

    await manager.broadcast_to_room(room_id=room_id, message=message)

    ws1.send_json.assert_awaited_once_with(message)
    ws2.send_json.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_broadcast_excludes_user(manager):
    room_id = uuid4()
    user1 = uuid4()
    user2 = uuid4()

    ws1 = AsyncMock()
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock()

    ws2 = AsyncMock()
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()

    await manager.connect(user_id=user1, websocket=ws1)
    await manager.connect(user_id=user2, websocket=ws2)

    manager.join_room(room_id=room_id, user_id=user1)
    manager.join_room(room_id=room_id, user_id=user2)

    message = {"type": "broadcast"}

    await manager.broadcast_to_room(
        room_id=room_id,
        message=message,
        exclude_user_id=user1,
    )

    ws1.send_json.assert_not_awaited()
    ws2.send_json.assert_awaited_once_with(message)
