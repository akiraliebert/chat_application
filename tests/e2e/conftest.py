import pytest_asyncio
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from app.main import app
from app.infrastructure.database.db import get_db_session
from app.config.settings import settings


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(settings.database_url, echo=True)
    async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def registered_user(client: AsyncClient):
    payload = {
        # делаем уникальным каждого юзера, чтобы не ловить уже существующих пользователей при scope = function(важно для test_auth_api)
        "email": f"e2e{uuid4()}@test.com",
        "password": "strong-password",
    }

    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201

    return payload


@pytest_asyncio.fixture
async def auth_tokens(client: AsyncClient, registered_user):
    response = await client.post(
        "/auth/login",
        json=registered_user,
    )

    assert response.status_code == 200
    data = response.json()

    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
    }
