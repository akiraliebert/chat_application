from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.db import get_db_session
from app.infrastructure.database.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork


async def get_uow(session: AsyncSession = Depends(get_db_session)):
    return SQLAlchemyUnitOfWork(session)
