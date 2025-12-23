from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.message_repository import MessageRepository

from app.infrastructure.database.repositories.message_repository import PostgresMessageRepository
from app.infrastructure.database.db import get_db_session


def get_message_repository(
    session: AsyncSession = Depends(get_db_session),
) -> MessageRepository:
    return PostgresMessageRepository(session)