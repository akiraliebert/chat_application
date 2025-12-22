import pytest
from unittest.mock import AsyncMock, Mock

from app.application.security.password_hasher import PasswordHasher
from app.domain.repositories.user_repository import UserRepository
from app.domain.entities.user import User
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password


@pytest.fixture
def user_repository():
    repo = AsyncMock(spec=UserRepository)
    repo.exists_by_email.return_value = False
    return repo


@pytest.fixture
def password_hasher():
    hasher = Mock(spec=PasswordHasher)
    hasher.verify.return_value = True
    hasher.hash.return_value = "hashed-password"
    return hasher


@pytest.fixture
def active_user():
    return User(
        user_id=UserId(),
        email=Email("test@example.com"),
        password=Password("hashed-password"),
        is_active=True,
    )


@pytest.fixture
def inactive_user():
    return User(
        user_id=UserId(),
        email=Email("test@example.com"),
        password=Password("hashed-password"),
        is_active=False,
    )
