import pytest
from uuid import uuid4
from datetime import timezone

from app.domain.entities.room import Room
from app.domain.enums.room_type import RoomType
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.room_name import RoomName


@pytest.mark.asyncio
async def test_add_and_get_public_room(room_repository, uow):
    owner_id = uuid4()

    room = Room(
        room_id=RoomId(),
        name=RoomName("Integration public room"),
        owner_id=owner_id,
        room_type=RoomType.PUBLIC,
    )

    async with uow:
        await room_repository.add(room)

    found = await room_repository.get_by_id(room.id)

    assert found is not None
    assert found.id == room.id
    assert found.name == room.name
    assert found.owner_id == owner_id
    assert found.room_type == RoomType.PUBLIC
    assert found.is_member(owner_id) is True
    assert found.created_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_add_and_get_private_room(room_repository, uow):
    user_a = uuid4()
    user_b = uuid4()

    room = Room(
        room_id=RoomId(),
        name=RoomName("Private integration chat"),
        owner_id=user_a,
        room_type=RoomType.PRIVATE,
        members={user_a, user_b},
    )

    async with uow:
        await room_repository.add(room)

    found = await room_repository.get_by_id(room.id)

    assert found is not None
    assert found.room_type == RoomType.PRIVATE
    assert found.is_member(user_a) is True
    assert found.is_member(user_b) is True
    assert len(found.members) == 2


@pytest.mark.asyncio
async def test_add_member_persists(room_repository, uow):
    owner_id = uuid4()
    new_user_id = uuid4()

    room = Room(
        room_id=RoomId(),
        name=RoomName("Integration room"),
        owner_id=owner_id,
        room_type=RoomType.PUBLIC,
    )

    async with uow:
        await room_repository.add(room)

    async with uow:
        await room_repository.add_member(room.id, new_user_id)

    found = await room_repository.get_by_id(room.id)

    assert found.is_member(new_user_id) is True


@pytest.mark.asyncio
async def test_exists_private_room(room_repository, uow):
    user_a = uuid4()
    user_b = uuid4()

    room = Room(
        room_id=RoomId(),
        name=RoomName("Private exists check"),
        owner_id=user_a,
        room_type=RoomType.PRIVATE,
        members={user_a, user_b},
    )

    async with uow:
        await room_repository.add(room)

    exists = await room_repository.exists_private_room(user_a, user_b)

    assert exists is True


@pytest.mark.asyncio
async def test_get_nonexistent_room_returns_none(room_repository):
    result = await room_repository.get_by_id(RoomId())

    assert result is None
