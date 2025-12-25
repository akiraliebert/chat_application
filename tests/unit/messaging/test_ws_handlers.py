import pytest
from unittest.mock import AsyncMock, patch, Mock
from uuid import uuid4

from app.domain.value_objects.user_id import UserId
from app.interfaces.websocket.handlers import (
    handle_join_room,
    handle_send_message,
    handle_typing,
)


@pytest.mark.asyncio
async def test_handle_typing_publishes_event():
    event_bus = AsyncMock()
    user_id = UserId(uuid4())
    room_id = uuid4()

    payload = {"room_id": str(room_id)}

    await handle_typing(
        event_bus=event_bus,
        user_id=user_id,
        payload=payload,
    )

    event_bus.publish.assert_awaited_once()
    event = event_bus.publish.call_args.args[0]

    assert event["message"]["type"] == "typing"


@pytest.mark.asyncio
async def test_handle_join_room_creates_system_message_and_publishes():
    event_bus = AsyncMock()
    manager = Mock()

    user_id = UserId(uuid4())
    room_id = uuid4()

    fake_message = AsyncMock()
    fake_message.id.value = uuid4()
    fake_message.content.value = "joined"
    fake_message.created_at.isoformat.return_value = "now"

    fake_uc = AsyncMock()
    fake_uc.execute.return_value = fake_message

    with patch(
        "app.interfaces.websocket.handlers.CreateSystemMessageUseCase",
        return_value=fake_uc,
    ):
        await handle_join_room(
            event_bus=event_bus,
            manager=manager,
            user_id=user_id,
            payload={"room_id": str(room_id)},
        )

    manager.join_room.assert_called_once()
    event_bus.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_send_message_creates_user_message_and_publishes():
    event_bus = AsyncMock()
    user_id = UserId(uuid4())
    room_id = uuid4()

    fake_message = AsyncMock()
    fake_message.id.value = uuid4()
    fake_message.room_id.value = room_id
    fake_message.sender_id.value = user_id.value
    fake_message.content.value = "hello"
    fake_message.created_at.isoformat.return_value = "now"

    fake_uc = AsyncMock()
    fake_uc.execute.return_value = fake_message

    with patch(
        "app.interfaces.websocket.handlers.CreateUserMessageUseCase",
        return_value=fake_uc,
    ):
        await handle_send_message(
            event_bus=event_bus,
            user_id=user_id,
            payload={
                "room_id": str(room_id),
                "content": "hello",
            },
        )

    event_bus.publish.assert_awaited_once()

