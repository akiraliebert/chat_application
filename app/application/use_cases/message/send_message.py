from app.application.uow.unit_of_work import UnitOfWork
from app.application.exceptions import RoomNotFoundError, UserNotInRoomError
from app.domain.entities.message import Message
from app.domain.enums.message_type import MessageType
from app.domain.repositories.message_repository import MessageRepository
from app.domain.repositories.room_repository import RoomRepository
from app.domain.value_objects.message_content import MessageContent
from app.domain.value_objects.message_id import MessageId
from app.domain.value_objects.room_id import RoomId
from app.domain.value_objects.user_id import UserId


class SendMessageUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        message_repository: MessageRepository,
        room_repository: RoomRepository,
    ):
        self._uow = uow
        self._message_repo = message_repository
        self._room_repo = room_repository

    async def execute(
        self,
        *,
        room_id: RoomId,
        sender_id: UserId,
        content: str,
    ) -> Message:
        async with self._uow:
            room = await self._room_repo.get_by_id(room_id)
            if room is None:
                raise RoomNotFoundError()

            if not room.is_member(sender_id.value):
                raise UserNotInRoomError()

            message = Message(
                message_id=MessageId(),
                room_id=room_id,
                sender_id=sender_id,
                content=MessageContent(content),
                message_type=MessageType.TEXT,
            )

            await self._message_repo.add(message)

            return message
