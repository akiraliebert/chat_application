from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List

from app.domain.enums.room_type import RoomType


class CreateRoomRequest(BaseModel):
    name: str
    room_type: RoomType
    second_user_id: UUID | None = None


class RoomResponse(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    room_type: RoomType
    members: List[UUID]
    created_at: datetime
