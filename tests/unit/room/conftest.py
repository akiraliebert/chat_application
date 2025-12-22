import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.domain.repositories.room_repository import RoomRepository
from app.domain.entities.room import Room
from app.domain.enums.room_type import RoomType
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.room_name import RoomName


@pytest.fixture
def room_repository():
    return AsyncMock(spec=RoomRepository)


@pytest.fixture
def owner_id():
    return uuid4()


@pytest.fixture
def second_user_id():
    return uuid4()


@pytest.fixture
def public_room(owner_id):
    return Room(
        room_id=RoomId(),
        name=RoomName("Public"),
        owner_id=owner_id,
        room_type=RoomType.PUBLIC,
    )
