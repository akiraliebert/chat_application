from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.models.base import Base
from app.domain.enums.room_type import RoomType


class RoomModel(Base):
    __tablename__ = "rooms"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(length=100),
        nullable=False,
    )

    owner_id: Mapped[UUID] = mapped_column(
        nullable=False,
    )

    room_type: Mapped[RoomType] = mapped_column(
        Enum(RoomType, name="room_type"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
