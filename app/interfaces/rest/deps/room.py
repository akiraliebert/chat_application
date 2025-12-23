from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.room.create_room import CreateRoomUseCase
from app.application.use_cases.room.join_room import JoinRoomUseCase

from app.domain.repositories.room_repository import RoomRepository

from app.infrastructure.database.repositories.room_repository import PostgresRoomRepository
from app.infrastructure.database.db import get_db_session

from app.interfaces.rest.deps.common import get_uow


def get_room_repository(
    session: AsyncSession = Depends(get_db_session),
) -> RoomRepository:
    return PostgresRoomRepository(session)


def get_create_room_use_case(
    uow=Depends(get_uow),
    room_repository: RoomRepository = Depends(get_room_repository),
) -> CreateRoomUseCase:
    return CreateRoomUseCase(uow=uow, room_repository=room_repository)


def get_join_room_use_case(
    uow=Depends(get_uow),
    room_repository: RoomRepository = Depends(get_room_repository),
) -> JoinRoomUseCase:
    return JoinRoomUseCase(uow=uow, room_repository=room_repository)
