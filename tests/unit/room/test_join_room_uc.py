import pytest
from uuid import uuid4

from app.application.use_cases.room.join_room import JoinRoomUseCase
from app.application.exceptions import RoomNotFoundError, UserAlreadyInRoomError


@pytest.mark.asyncio
async def test_join_room_success(
    uow,
    room_repository,
    public_room,
):
    new_user_id = uuid4()
    room_repository.get_by_id.return_value = public_room

    use_case = JoinRoomUseCase(
        uow=uow,
        room_repository=room_repository,
    )

    await use_case.execute(
        room_id=public_room.id.value,
        user_id=new_user_id,
    )

    assert public_room.is_member(new_user_id) is True
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_join_room_not_found(
    uow,
    room_repository,
):
    room_repository.get_by_id.return_value = None

    use_case = JoinRoomUseCase(
        uow=uow,
        room_repository=room_repository,
    )

    with pytest.raises(RoomNotFoundError):
        await use_case.execute(
            room_id=uuid4(),
            user_id=uuid4(),
        )

    assert uow.committed is False
    assert uow.rolled_back is True


@pytest.mark.asyncio
async def test_join_room_user_already_member(
    uow,
    room_repository,
    public_room,
):
    existing_user_id = next(iter(public_room.members))
    room_repository.get_by_id.return_value = public_room

    use_case = JoinRoomUseCase(
        uow=uow,
        room_repository=room_repository,
    )

    with pytest.raises(UserAlreadyInRoomError):
        await use_case.execute(
            room_id=public_room.id.value,
            user_id=existing_user_id,
        )

    assert uow.committed is False
    assert uow.rolled_back is True
