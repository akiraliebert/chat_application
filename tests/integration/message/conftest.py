import pytest_asyncio
from uuid import uuid4

from app.domain.value_objects.room_id import RoomId
from app.domain.entities.room import Room
from app.domain.enums.room_type import RoomType
from app.domain.value_objects.room_name import RoomName


@pytest_asyncio.fixture
async def room(uow, room_repository):
    #  сетапим комнату
    room = Room(
        room_id=RoomId(),
        name=RoomName("Integration public room"),
        owner_id=uuid4(),
        room_type=RoomType.PUBLIC,
    )

    async with uow:
        await room_repository.add(room)
    return room

