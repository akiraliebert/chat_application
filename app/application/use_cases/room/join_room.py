from uuid import UUID

from app.application.uow.unit_of_work import UnitOfWork
from app.application.exceptions import RoomNotFoundError, UserAlreadyInRoomError
from app.domain.repositories.room_repository import RoomRepository
from app.domain.value_objects.room_id import RoomId


class JoinRoomUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        room_repository: RoomRepository,
    ):
        self._uow = uow
        self._room_repository = room_repository

    async def execute(
        self,
        *,
        room_id: UUID,
        user_id: UUID,
    ) -> None:
        async with self._uow:
            room = await self._room_repository.get_by_id(RoomId(room_id))
            if room is None:
                raise RoomNotFoundError()

            if room.is_member(user_id):
                raise UserAlreadyInRoomError()

            room.add_member(user_id)
