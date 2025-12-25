from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password

from app.infrastructure.database.models.user_model import UserModel


class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, user: User) -> None:
        model = UserModel(
            id=user.id.value,
            email=user.email.value,
            password_hash=user.password.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        self._session.add(model)

    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def get_by_email(self, email: Email) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def exists_by_email(self, email: Email) -> bool:
        stmt = select(UserModel.id).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        return result.first() is not None

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            user_id=UserId(model.id),
            email=Email(model.email),
            password=Password(model.password_hash),
            is_active=model.is_active,
            created_at=model.created_at,
        )
