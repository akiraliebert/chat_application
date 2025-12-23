from abc import ABC, abstractmethod
from typing import Iterable

from app.domain.entities.message import Message
from app.domain.value_objects.room_id import RoomId


class MessageRepository(ABC):

    @abstractmethod
    async def add(self, message: Message) -> None:
        ...

    @abstractmethod
    async def get_room_history(
        self,
        room_id: RoomId,
        *,
        limit: int,
        offset: int,
    ) -> Iterable[Message]:
        ...
