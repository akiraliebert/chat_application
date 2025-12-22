from datetime import datetime, timezone
from uuid import UUID

from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.room_name import RoomName
from app.domain.enums.room_type import RoomType
from app.domain.exceptions import DomainError, UserNotInRoomError, UserAlreadyInRoomError


class Room:
    def __init__(
        self,
        room_id: RoomId,
        name: RoomName,
        owner_id: UUID,
        room_type: RoomType,
        members: set[UUID] | None = None,
        created_at: datetime | None = None,
    ):
        self._id = room_id
        self._name = name
        self._owner_id = owner_id
        self._type = room_type
        self._members = members or {owner_id}
        self._created_at = created_at or datetime.now(timezone.utc)

        if self._type == RoomType.PRIVATE and len(self._members) != 2:
            raise DomainError("Private room must have exactly two members")

    @property
    def id(self) -> RoomId:
        return self._id

    @property
    def name(self) -> RoomName:
        return self._name

    @property
    def owner_id(self) -> UUID:
        return self._owner_id

    @property
    def room_type(self) -> RoomType:
        return self._type

    @property
    def members(self) -> set[UUID]:
        return set(self._members)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def is_member(self, user_id: UUID) -> bool:
        return user_id in self._members

    def add_member(self, user_id: UUID) -> None:
        if self.is_member(user_id):
            raise UserAlreadyInRoomError()
        if self._type == RoomType.PRIVATE:
            raise DomainError("Cannot add members to private room")

        self._members.add(user_id)

    def remove_member(self, user_id: UUID) -> None:
        if not self.is_member(user_id):
            raise UserNotInRoomError()

        if user_id == self._owner_id:
            raise DomainError("Owner cannot leave the room")

        self._members.remove(user_id)
