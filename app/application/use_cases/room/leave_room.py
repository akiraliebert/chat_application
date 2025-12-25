from uuid import UUID

from app.application.uow.unit_of_work import UnitOfWork
from app.application.exceptions import RoomNotFoundError, UserNotInRoomError
from app.domain.repositories.room_repository import RoomRepository
from app.domain.value_objects.room_id import RoomId


class LeaveRoomUseCase:
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

            if not room.is_member(user_id):
                raise UserNotInRoomError()

            room.remove_member(user_id)

            await self._room_repository.remove_member(room.id, user_id)
