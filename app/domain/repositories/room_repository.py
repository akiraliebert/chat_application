from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.room import Room
from app.domain.value_objects.room_id import RoomId


class RoomRepository(ABC):

    @abstractmethod
    async def add(self, room: Room) -> None:
        ...

    @abstractmethod
    async def get_by_id(self, room_id: RoomId) -> Optional[Room]:
        ...

    @abstractmethod
    async def exists_private_room(self, user_a_id, user_b_id) -> bool:
        ...

    @abstractmethod
    async def add_member(self, room_id: RoomId, user_id: UUID) -> None:
        ...

    @abstractmethod
    async def remove_member(self, room_id: RoomId, user_id: UUID) -> None:
        ...
