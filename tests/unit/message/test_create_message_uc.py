import pytest

from app.application.use_cases.message.create_user_message import CreateUserMessageUseCase
from app.application.exceptions import RoomNotFoundError, UserNotInRoomError
from app.domain.entities.message import Message
from app.domain.value_objects.room_id import RoomId


@pytest.mark.asyncio
async def test_send_message_success(
    uow,
    message_repository,
    room_repository,
    room,
    owner_id,
):
    room_repository.get_by_id.return_value = room

    use_case = CreateUserMessageUseCase(
        uow=uow,
        message_repository=message_repository,
        room_repository=room_repository,
    )

    message = await use_case.execute(
        room_id=room.id,
        sender_id=owner_id,
        content="Hello from unit test",
    )

    room_repository.get_by_id.assert_awaited_once_with(room.id)
    message_repository.add.assert_awaited_once()
    assert isinstance(message, Message)
    assert message.content.value == "Hello from unit test"
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_send_message_room_not_found(
    uow,
    message_repository,
    room_repository,
    owner_id,
):
    room_repository.get_by_id.return_value = None

    use_case = CreateUserMessageUseCase(
        uow=uow,
        message_repository=message_repository,
        room_repository=room_repository,
    )

    with pytest.raises(RoomNotFoundError):
        await use_case.execute(
            room_id=RoomId(),
            sender_id=owner_id,
            content="Hello",
        )

    message_repository.add.assert_not_called()
    assert uow.committed is False
    assert uow.rolled_back is True


@pytest.mark.asyncio
async def test_send_message_user_not_in_room(
    uow,
    message_repository,
    room_repository,
    room,
    outsider_id,
):
    room_repository.get_by_id.return_value = room

    use_case = CreateUserMessageUseCase(
        uow=uow,
        message_repository=message_repository,
        room_repository=room_repository,
    )

    with pytest.raises(UserNotInRoomError):
        await use_case.execute(
            room_id=room.id,
            sender_id=outsider_id,
            content="I should not be here",
        )

    message_repository.add.assert_not_called()
    assert uow.committed is False
    assert uow.rolled_back is True
