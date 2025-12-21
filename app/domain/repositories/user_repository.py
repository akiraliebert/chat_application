from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.user import User
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.email import Email


class UserRepository(ABC):

    @abstractmethod
    async def add(self, user: User) -> None:
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        ...

    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        ...

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        ...
