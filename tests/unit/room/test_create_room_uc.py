import pytest

from app.application.use_cases.room.create_room import CreateRoomUseCase
from app.application.exceptions import RoomAlreadyExistsError
from app.domain.enums.room_type import RoomType


@pytest.mark.asyncio
async def test_create_public_room_success(
    uow,
    room_repository,
    owner_id,
):
    use_case = CreateRoomUseCase(
        uow=uow,
        room_repository=room_repository,
    )

    room = await use_case.execute(
        name="Public room",
        owner_id=owner_id,
        room_type=RoomType.PUBLIC,
    )

    room_repository.add.assert_awaited_once()
    assert room.owner_id == owner_id
    assert room.room_type == RoomType.PUBLIC
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_create_private_room_success(
    uow,
    room_repository,
    owner_id,
    second_user_id,
):
    room_repository.exists_private_room.return_value = False

    use_case = CreateRoomUseCase(
        uow=uow,
        room_repository=room_repository,
    )

    room = await use_case.execute(
        name="Private chat",
        owner_id=owner_id,
        room_type=RoomType.PRIVATE,
        second_user_id=second_user_id,
    )

    room_repository.exists_private_room.assert_awaited_once_with(
        owner_id,
        second_user_id,
    )
    assert room.room_type == RoomType.PRIVATE
    assert uow.committed is True


@pytest.mark.asyncio
async def test_create_private_room_already_exists(
    uow,
    room_repository,
    owner_id,
    second_user_id,
):
    room_repository.exists_private_room.return_value = True

    use_case = CreateRoomUseCase(
        uow=uow,
        room_repository=room_repository,
    )

    with pytest.raises(RoomAlreadyExistsError):
        await use_case.execute(
            name="Private chat",
            owner_id=owner_id,
            room_type=RoomType.PRIVATE,
            second_user_id=second_user_id,
        )

    room_repository.add.assert_not_called()
    assert uow.committed is False
    assert uow.rolled_back is True
