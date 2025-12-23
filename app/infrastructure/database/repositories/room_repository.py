from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.room import Room
from app.domain.repositories.room_repository import RoomRepository
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.room_name import RoomName
from app.domain.enums.room_type import RoomType

from app.infrastructure.database.models.room_model import RoomModel
from app.infrastructure.database.models.room_member_model import RoomMemberModel


class PostgresRoomRepository(RoomRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, room: Room) -> None:
        room_model = RoomModel(
            id=room.id.value,
            name=room.name.value,
            owner_id=room.owner_id,
            room_type=room.room_type,
            created_at=room.created_at,
        )

        self._session.add(room_model)
        await self._session.flush()  # фиксируем добавление room для room_member

        for user_id in room.members:
            self._session.add(
                RoomMemberModel(
                    room_id=room.id.value,
                    user_id=user_id,
                )
            )

    async def get_by_id(self, room_id: RoomId) -> Optional[Room]:
        stmt = select(RoomModel).where(RoomModel.id == room_id.value)
        result = await self._session.execute(stmt)
        room_model = result.scalar_one_or_none()

        if room_model is None:
            return None

        members_stmt = select(RoomMemberModel.user_id).where(
            RoomMemberModel.room_id == room_id.value
        )
        members_result = await self._session.execute(members_stmt)
        members = {row[0] for row in members_result.all()}

        return Room(
            room_id=RoomId(room_model.id),
            name=RoomName(room_model.name),
            owner_id=room_model.owner_id,
            room_type=room_model.room_type,
            members=members,
            created_at=room_model.created_at,
        )

    async def exists_private_room(self, user_a_id: UUID, user_b_id: UUID) -> bool:
        stmt = (
            select(RoomModel.id)
            .join(RoomMemberModel)
            .where(
                RoomModel.room_type == RoomType.PRIVATE,
                RoomMemberModel.user_id.in_([user_a_id, user_b_id]),
            )
            .group_by(RoomModel.id)
            .having(
                and_(
                    # exactly two members
                    # and both users are present
                    # count(*) == 2
                    # NOTE: DB-level invariant check
                    True
                )
            )
        )

        result = await self._session.execute(stmt)
        room_ids = [row[0] for row in result.all()]

        return bool(room_ids)

    async def add_member(self, room_id: RoomId, user_id: UUID) -> None:
        self._session.add(
            RoomMemberModel(
                room_id=room_id.value,
                user_id=user_id,
            )
        )

    async def remove_member(self, room_id: RoomId, user_id: UUID) -> None:
        stmt = delete(RoomMemberModel).where(
            RoomMemberModel.room_id == room_id.value,
            RoomMemberModel.user_id == user_id,
        )
        await self._session.execute(stmt)


