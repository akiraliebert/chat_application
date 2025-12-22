from abc import ABC, abstractmethod
from typing import Optional

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
