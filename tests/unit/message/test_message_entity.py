import pytest
from datetime import timezone

from app.domain.entities.message import Message
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.message_content import (
    MessageContent,
    InvalidMessageContentError,
)
from app.domain.enums.message_type import MessageType
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.user_id import UserId
from app.domain.exceptions import DomainError


def test_create_text_message_success():
    message = Message(
        message_id=MessageId(),
        room_id=RoomId(),
        sender_id=UserId(),
        content=MessageContent("Hello world"),
        message_type=MessageType.TEXT,
    )

    assert message.message_type == MessageType.TEXT
    assert message.sender_id is not None
    assert message.content.value == "Hello world"
    assert message.created_at.tzinfo == timezone.utc


def test_create_system_message_success():
    message = Message(
        message_id=MessageId(),
        room_id=RoomId(),
        sender_id=None,
        content=MessageContent("User joined the room"),
        message_type=MessageType.SYSTEM,
    )

    assert message.message_type == MessageType.SYSTEM
    assert message.sender_id is None
    assert message.content.value == "User joined the room"


def test_text_message_without_sender_raises_error():
    with pytest.raises(DomainError):
        Message(
            message_id=MessageId(),
            room_id=RoomId(),
            sender_id=None,
            content=MessageContent("Invalid"),
            message_type=MessageType.TEXT,
        )


def test_system_message_with_sender_raises_error():
    with pytest.raises(DomainError):
        Message(
            message_id=MessageId(),
            room_id=RoomId(),
            sender_id=UserId(),
            content=MessageContent("Invalid"),
            message_type=MessageType.SYSTEM,
        )


def test_message_content_cannot_be_empty():
    with pytest.raises(InvalidMessageContentError):
        MessageContent("   ")


def test_message_content_too_long_raises_error():
    with pytest.raises(InvalidMessageContentError):
        MessageContent("a" * 4001)


def test_message_ids_and_refs_are_value_objects():
    message = Message(
        message_id=MessageId(),
        room_id=RoomId(),
        sender_id=UserId(),
        content=MessageContent("VO test"),
    )

    assert isinstance(message.id, MessageId)
    assert isinstance(message.room_id, RoomId)
    assert isinstance(message.sender_id, UserId)


def test_message_created_at_is_immutable():
    message = Message(
        message_id=MessageId(),
        room_id=RoomId(),
        sender_id=UserId(),
        content=MessageContent("Time test"),
    )

    created_at = message.created_at

    # нет сеттера → нельзя изменить
    with pytest.raises(AttributeError):
        message.created_at = created_at
