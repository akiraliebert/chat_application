import pytest
from unittest.mock import AsyncMock

from app.domain.repositories.message_repository import MessageRepository
from app.domain.repositories.room_repository import RoomRepository
from app.domain.entities.room import Room
from app.domain.enums.room_type import RoomType
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.room_name import RoomName
from app.domain.value_objects.user_id import UserId


@pytest.fixture
def message_repository():
    return AsyncMock(spec=MessageRepository)


@pytest.fixture
def room_repository():
    return AsyncMock(spec=RoomRepository)


@pytest.fixture
def room(owner_id):
    return Room(
        room_id=RoomId(),
        name=RoomName("Room for messages"),
        owner_id=owner_id.value,
        room_type=RoomType.PUBLIC,
    )


@pytest.fixture
def owner_id():
    return UserId()


@pytest.fixture
def outsider_id():
    return UserId()
