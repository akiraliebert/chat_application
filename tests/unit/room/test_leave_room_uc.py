import pytest
from uuid import uuid4

from app.application.use_cases.room.leave_room import LeaveRoomUseCase
from app.application.exceptions import RoomNotFoundError, UserNotInRoomError


@pytest.mark.asyncio
async def test_leave_room_success(
    uow,
    room_repository,
    public_room,
):
    new_user_id = uuid4()
    public_room.add_member(new_user_id)
    room_repository.get_by_id.return_value = public_room


    use_case = LeaveRoomUseCase(
        uow=uow,
        room_repository=room_repository
    )

    await use_case.execute(
        room_id=public_room.id.value,
        user_id=new_user_id,
    )

    assert public_room.is_member(new_user_id) is False
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_leave_room_not_found(
    uow,
    room_repository,
):
    room_repository.get_by_id.return_value = None

    use_case = LeaveRoomUseCase(
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
async def test_leave_room_user_not_in_room(
    uow,
    room_repository,
    public_room,
):
    room_repository.get_by_id.return_value = public_room

    use_case = LeaveRoomUseCase(
        uow=uow,
        room_repository=room_repository,
    )

    with pytest.raises(UserNotInRoomError):
        await use_case.execute(
            room_id=public_room.id.value,
            user_id=uuid4(),
        )

    assert uow.committed is False
    assert uow.rolled_back is True
