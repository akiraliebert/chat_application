from uuid import UUID

from app.application.uow.unit_of_work import UnitOfWork
from app.application.exceptions import RoomAlreadyExistsError
from app.domain.entities.room import Room
from app.domain.enums.room_type import RoomType
from app.domain.repositories.room_repository import RoomRepository
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.room_name import RoomName


class CreateRoomUseCase:
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
        name: str,
        owner_id: UUID,
        room_type: RoomType,
        second_user_id: UUID | None = None,
    ) -> Room:
        async with self._uow:
            if room_type == RoomType.PRIVATE:
                if second_user_id is None:
                    raise ValueError("second_user_id is required for private room")

                exists = await self._room_repository.exists_private_room(
                    owner_id,
                    second_user_id,
                )
                if exists:
                    raise RoomAlreadyExistsError()

                members = {owner_id, second_user_id}
            else:
                members = None

            room = Room(
                room_id=RoomId(),
                name=RoomName(name),
                owner_id=owner_id,
                room_type=room_type,
                members=members,
            )

            await self._room_repository.add(room)

            return room
