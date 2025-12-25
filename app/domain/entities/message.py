from datetime import datetime, timezone

from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.message_content import MessageContent
from app.domain.enums.message_type import MessageType
from app.domain.exceptions import DomainError


class Message:
    def __init__(
        self,
        message_id: MessageId,
        room_id: RoomId,
        sender_id: UserId | None,
        content: MessageContent,
        message_type: MessageType = MessageType.TEXT,
        created_at: datetime | None = None,
    ):
        if message_type == MessageType.SYSTEM and sender_id is not None:
            raise DomainError("System message cannot have sender")

        if message_type == MessageType.TEXT and sender_id is None:
            raise DomainError("Text message must have sender")

        self._id = message_id
        self._room_id = room_id
        self._sender_id = sender_id
        self._content = content
        self._type = message_type
        self._created_at = created_at or datetime.now(timezone.utc)

    @property
    def id(self) -> MessageId:
        return self._id

    @property
    def room_id(self) -> RoomId:
        return self._room_id

    @property
    def sender_id(self) -> UserId | None:
        return self._sender_id

    @property
    def content(self) -> MessageContent:
        return self._content

    @property
    def message_type(self) -> MessageType:
        return self._type

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @classmethod
    def system(
            cls,
            *,
            room_id,
            content: str,
    ) -> "Message":
        return cls(
            message_id=MessageId(),
            room_id=room_id,
            sender_id=None,
            content=MessageContent(content),
            message_type=MessageType.SYSTEM,
        )
