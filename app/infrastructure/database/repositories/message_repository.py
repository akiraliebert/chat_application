from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.message import Message
from app.domain.repositories.message_repository import MessageRepository
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.message_content import MessageContent
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.user_id import UserId
from app.domain.enums.message_type import MessageType

from app.infrastructure.database.models.message_model import MessageModel


class PostgresMessageRepository(MessageRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, message: Message) -> None:
        self._session.add(
            MessageModel(
                id=message.id.value,
                room_id=message.room_id.value,
                sender_id=message.sender_id.value
                if message.sender_id is not None
                else None,
                content=message.content.value,
                message_type=message.message_type,
                created_at=message.created_at,
            )
        )

    async def get_room_history(
        self,
        room_id: RoomId,
        *,
        limit: int,
        offset: int,
    ) -> Iterable[Message]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.room_id == room_id.value)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self._session.execute(stmt)
        rows = result.scalars().all()

        return [
            Message(
                message_id=MessageId(row.id),
                room_id=RoomId(row.room_id),
                sender_id=UserId(row.sender_id)
                if row.sender_id is not None
                else None,
                content=MessageContent(row.content),
                message_type=MessageType(row.message_type),
                created_at=row.created_at,
            )
            for row in rows
        ]
