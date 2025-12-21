from datetime import datetime, timezone

from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.exceptions import (
    UserAlreadyActiveError,
    UserAlreadyInactiveError,
)


class User:
    def __init__(
        self,
        user_id: UserId,
        email: Email,
        password: Password,
        is_active: bool = True,
        is_online: bool = False,
        created_at: datetime | None = None,
    ):
        self._id = user_id
        self._email = email
        self._password = password
        self._is_active = is_active
        self._is_online = is_online
        self._created_at = created_at or datetime.now(timezone.utc)

    @property
    def id(self) -> UserId:
        return self._id

    @property
    def email(self) -> Email:
        return self._email

    @property
    def password(self) -> Password:
        return self._password

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_online(self) -> bool:
        return self._is_online

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def activate(self) -> None:
        if self._is_active:
            raise UserAlreadyActiveError()
        self._is_active = True

    def deactivate(self) -> None:
        if not self._is_active:
            raise UserAlreadyInactiveError()
        self._is_active = False
        self._is_online = False

    def go_online(self) -> None:
        if not self._is_active:
            raise UserAlreadyInactiveError()
        self._is_online = True

    def go_offline(self) -> None:
        self._is_online = False
