from app.application.uow.unit_of_work import UnitOfWork
from app.domain.entities.message import Message
from app.domain.repositories.message_repository import MessageRepository
from app.domain.value_objects.room_id import RoomId


class CreateSystemMessageUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        message_repository: MessageRepository,
    ):
        self._uow = uow
        self._message_repo = message_repository

    async def execute(
        self,
        *,
        room_id: RoomId,
        content: str,
    ) -> Message:
        async with self._uow:
            message = Message.system(
                room_id=room_id,
                content=content,
            )

            await self._message_repo.add(message)

            return message
