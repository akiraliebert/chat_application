from fastapi import APIRouter, Depends, HTTPException, Query, status
from uuid import UUID

from app.interfaces.rest.schemas.message_schema import (
    MessageListResponse,
    MessageResponse,
)
from app.interfaces.rest.deps.message import (
    get_message_repository,
)
from app.interfaces.rest.deps.room import (
    get_room_repository,
)
from app.interfaces.rest.deps.user import get_current_user

from app.domain.entities.user import User
from app.domain.value_objects.room_id import RoomId


router = APIRouter(prefix="/rooms", tags=["messages"])


@router.get(
    "/{room_id}/messages",
    response_model=MessageListResponse,
)
async def get_room_messages(
    room_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    message_repository=Depends(get_message_repository),
    room_repository=Depends(get_room_repository),
):
    room = await room_repository.get_by_id(RoomId(room_id))

    if room is None or not room.is_member(current_user.id.value):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    messages = await message_repository.get_room_history(
        room_id=RoomId(room_id),
        limit=limit,
        offset=offset,
    )

    return MessageListResponse(
        items=[
            MessageResponse(
                id=msg.id.value,
                room_id=msg.room_id.value,
                sender_id=msg.sender_id.value if msg.sender_id else None,
                content=msg.content.value,
                message_type=msg.message_type,
                created_at=msg.created_at,
            )
            for msg in messages
        ],
        limit=limit,
        offset=offset,
    )
