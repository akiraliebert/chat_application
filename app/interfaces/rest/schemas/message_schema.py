from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.message_type import MessageType


class MessageResponse(BaseModel):
    id: UUID
    room_id: UUID
    sender_id: UUID | None
    content: str
    message_type: MessageType
    created_at: datetime


class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    limit: int
    offset: int
