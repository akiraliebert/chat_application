from abc import ABC, abstractmethod
from uuid import UUID


class JWTService(ABC):

    @abstractmethod
    def create_access_token(self, user_id: UUID) -> str:
        ...

    @abstractmethod
    def create_refresh_token(self, user_id: UUID) -> str:
        ...

    @abstractmethod
    def verify_access_token(self, token: str) -> UUID:
        ...

    @abstractmethod
    def verify_refresh_token(self, token: str) -> UUID:
        ...
