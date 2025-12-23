import pytest

from app.domain.entities.message import Message
from app.domain.enums.message_type import MessageType
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.message_content import MessageContent
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.user_id import UserId


@pytest.mark.asyncio
async def test_add_and_get_single_message(
    db_session,
    uow,
    room_repository,
    message_repository,
    room
):
    sender_id = UserId(room.owner_id)

    message = Message(
        message_id=MessageId(),
        room_id=RoomId(room.id.value),
        sender_id=UserId(room.owner_id),
        content=MessageContent("Hello integration"),
    )

    async with uow:
        await message_repository.add(message)

    history = await message_repository.get_room_history(
        room_id=RoomId(room.id.value),
        limit=10,
        offset=0,
    )

    assert len(history) == 1
    stored = history[0]

    assert stored.id == message.id
    assert stored.room_id == RoomId(room.id.value)
    assert stored.sender_id == sender_id
    assert stored.content == message.content
    assert stored.message_type == MessageType.TEXT


@pytest.mark.asyncio
async def test_message_history_order_and_pagination(
    db_session,
    uow,
    message_repository,
    room
):
    sender_id = UserId(room.owner_id)

    messages = [
        Message(
            message_id=MessageId(),
            room_id=RoomId(room.id.value),
            sender_id=sender_id,
            content=MessageContent(f"msg {i}"),
        )
        for i in range(5)
    ]

    async with uow:
        for msg in messages:
            await message_repository.add(msg)

    history = await message_repository.get_room_history(
        room_id=RoomId(room.id.value),
        limit=3,
        offset=0,
    )

    assert len(history) == 3

    # DESC ordering: последнее сообщение — первое
    assert history[0].content.value == "msg 4"
    assert history[1].content.value == "msg 3"
    assert history[2].content.value == "msg 2"

    next_page = await message_repository.get_room_history(
        room_id=RoomId(room.id.value),
        limit=3,
        offset=3,
    )

    assert len(next_page) == 2
    assert next_page[0].content.value == "msg 1"
    assert next_page[1].content.value == "msg 0"


@pytest.mark.asyncio
async def test_system_message_persistence(
    db_session,
    uow,
    message_repository,
    room
):

    system_message = Message(
        message_id=MessageId(),
        room_id=RoomId(room.id.value),
        sender_id=None,
        content=MessageContent("User joined"),
        message_type=MessageType.SYSTEM,
    )

    async with uow:
        await message_repository.add(system_message)

    history = await message_repository.get_room_history(
        room_id=RoomId(room.id.value),
        limit=10,
        offset=0,
    )

    assert len(history) == 1
    msg = history[0]

    assert msg.message_type == MessageType.SYSTEM
    assert msg.sender_id is None
    assert msg.content.value == "User joined"
