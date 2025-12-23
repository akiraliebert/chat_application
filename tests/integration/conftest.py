import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from app.infrastructure.database.repositories.user_repository import PostgresUserRepository
from app.infrastructure.database.repositories.room_repository import PostgresRoomRepository
from app.infrastructure.database.repositories.message_repository import PostgresMessageRepository
from app.config.settings import settings


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(settings.database_url, echo=True)
    async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
def uow(db_session: AsyncSession):
    return SQLAlchemyUnitOfWork(db_session)


@pytest_asyncio.fixture
def user_repository(db_session: AsyncSession):
    return PostgresUserRepository(db_session)


@pytest_asyncio.fixture
def room_repository(db_session: AsyncSession):
    return PostgresRoomRepository(db_session)


@pytest_asyncio.fixture
def message_repository(db_session: AsyncSession):
    return PostgresMessageRepository(db_session)
