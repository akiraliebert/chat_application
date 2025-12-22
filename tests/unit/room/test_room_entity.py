import pytest
from uuid import uuid4
from datetime import timezone

from app.domain.entities.room import (
    Room,
    UserAlreadyInRoomError,
    UserNotInRoomError,
)
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.room_name import RoomName
from app.domain.enums.room_type import RoomType
from app.domain.exceptions import DomainError


def create_public_room(owner_id=None):
    owner_id = owner_id or uuid4()
    return Room(
        room_id=RoomId(),
        name=RoomName("Public room"),
        owner_id=owner_id,
        room_type=RoomType.PUBLIC,
    )


def create_private_room(user_a, user_b):
    return Room(
        room_id=RoomId(),
        name=RoomName("Private chat"),
        owner_id=user_a,
        room_type=RoomType.PRIVATE,
        members={user_a, user_b},
    )


def test_public_room_created_with_owner_as_member():
    owner_id = uuid4()

    room = create_public_room(owner_id)

    assert room.owner_id == owner_id
    assert room.is_member(owner_id) is True
    assert room.room_type == RoomType.PUBLIC
    assert room.created_at.tzinfo == timezone.utc


def test_private_room_must_have_exactly_two_members():
    user_a = uuid4()

    with pytest.raises(DomainError):
        Room(
            room_id=RoomId(),
            name=RoomName("Invalid private"),
            owner_id=user_a,
            room_type=RoomType.PRIVATE,
            members={user_a},
        )


def test_add_member_to_public_room():
    room = create_public_room()
    new_user = uuid4()

    room.add_member(new_user)

    assert room.is_member(new_user) is True


def test_add_existing_member_raises_error():
    room = create_public_room()
    user_id = next(iter(room.members))

    with pytest.raises(UserAlreadyInRoomError):
        room.add_member(user_id)


def test_cannot_add_member_to_private_room():
    user_a = uuid4()
    user_b = uuid4()
    user_c = uuid4()

    room = create_private_room(user_a, user_b)

    with pytest.raises(DomainError):
        room.add_member(user_c)


def test_remove_member_from_public_room():
    room = create_public_room()
    user_id = uuid4()
    room.add_member(user_id)

    room.remove_member(user_id)

    assert room.is_member(user_id) is False


def test_remove_nonexistent_member_raises_error():
    room = create_public_room()
    user_id = uuid4()

    with pytest.raises(UserNotInRoomError):
        room.remove_member(user_id)


def test_owner_cannot_leave_room():
    owner_id = uuid4()
    room = create_public_room(owner_id)

    with pytest.raises(DomainError):
        room.remove_member(owner_id)


def test_members_are_returned_as_copy():
    room = create_public_room()
    members = room.members
    members.clear()

    assert len(room.members) == 1
