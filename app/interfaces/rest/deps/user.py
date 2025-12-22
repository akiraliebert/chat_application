from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID

from app.domain.value_objects.user_id import UserId
from app.infrastructure.database.db import get_db_session
from app.infrastructure.database.repositories.user_repository import PostgresUserRepository
from app.infrastructure.database.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from app.infrastructure.security.password_hasher import BCryptPasswordHasher
from app.infrastructure.security.jwt_service import JoseJWTService
from app.application.security.password_hasher import PasswordHasher
from app.application.security.jwt_service import JWTService
from app.infrastructure.security.jwt_service import JWTErrorInvalidToken
from app.domain.repositories.user_repository import UserRepository


async def get_uow(session: AsyncSession = Depends(get_db_session)):
    return SQLAlchemyUnitOfWork(session)


async def get_user_repository(session: AsyncSession = Depends(get_db_session)):
    return PostgresUserRepository(session)


def get_password_hasher() -> PasswordHasher:
    return BCryptPasswordHasher()


def get_jwt_service() -> JWTService:
    return JoseJWTService()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    jwt_service: JWTService = Depends(get_jwt_service),
    user_repo: UserRepository = Depends(get_user_repository),
):
    try:
        user_id: UUID = jwt_service.verify_access_token(token)
    except JWTErrorInvalidToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = await user_repo.get_by_id(UserId(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user
