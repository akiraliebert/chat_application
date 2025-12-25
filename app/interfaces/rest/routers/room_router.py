from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.interfaces.rest.schemas.room_schema import (
    CreateRoomRequest,
    RoomResponse,
)
from app.interfaces.rest.deps.room import (
    get_create_room_use_case,
    get_join_room_use_case,
    get_leave_room_use_case,
    get_room_repository,
)
from app.interfaces.rest.deps.user import get_current_user

from app.domain.entities.user import User
from app.domain.value_objects.room_id import RoomId

from app.application.use_cases.room.create_room import CreateRoomUseCase
from app.application.use_cases.room.join_room import JoinRoomUseCase
from app.application.use_cases.room.leave_room import LeaveRoomUseCase
from app.application.exceptions import (
    RoomAlreadyExistsError,
    RoomNotFoundError,
    UserAlreadyInRoomError,
    SecondUserIsRequired,
    UserNotInRoomError
)


router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post(
    "",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_room(
    data: CreateRoomRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateRoomUseCase = Depends(get_create_room_use_case),
):
    try:
        room = await use_case.execute(
            name=data.name,
            owner_id=current_user.id.value,
            room_type=data.room_type,
            second_user_id=data.second_user_id,
        )
    except SecondUserIsRequired:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="second_user_id is required for private room",
        )
    except RoomAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Private room already exists",
        )

    return RoomResponse(
        id=room.id.value,
        name=room.name.value,
        owner_id=room.owner_id,
        room_type=room.room_type,
        members=list(room.members),
        created_at=room.created_at,
    )


@router.post(
    "/{room_id}/join",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def join_room(
    room_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: JoinRoomUseCase = Depends(get_join_room_use_case),
):
    try:
        await use_case.execute(
            room_id=room_id,
            user_id=current_user.id.value,
        )
    except RoomNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    except UserAlreadyInRoomError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already in room",
        )


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
)
async def get_room(
    room_id: UUID,
    current_user: User = Depends(get_current_user),
    room_repository=Depends(get_room_repository),
):
    room = await room_repository.get_by_id(room_id=RoomId(room_id))

    if room is None or not room.is_member(current_user.id.value):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return RoomResponse(
        id=room.id.value,
        name=room.name.value,
        owner_id=room.owner_id,
        room_type=room.room_type,
        members=list(room.members),
        created_at=room.created_at,
    )


@router.post(
    "/{room_id}/leave",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def leave_room(
    room_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: LeaveRoomUseCase = Depends(get_leave_room_use_case),
):
    try:
        await use_case.execute(
            room_id=room_id,
            user_id=current_user.id.value,
        )
    except RoomNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    except UserNotInRoomError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User not found in room",
        )

