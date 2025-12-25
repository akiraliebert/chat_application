import pytest
from datetime import timezone

from app.domain.entities.user import User
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.exceptions import (
    InvalidEmailError,
    UserAlreadyActiveError,
    UserAlreadyInactiveError,
)


def create_user():
    return User(
        user_id=UserId(),
        email=Email("test@example.com"),
        password=Password("hashed-password"),
    )


def test_user_created_successfully():
    user = create_user()

    assert user.is_active is True
    assert user.email.value == "test@example.com"
    assert user.created_at.tzinfo == timezone.utc


def test_invalid_email_raises_error():
    with pytest.raises(InvalidEmailError):
        Email("invalid-email")


def test_user_deactivate_success():
    user = create_user()

    user.deactivate()

    assert user.is_active is False


def test_deactivate_inactive_user_raises():
    user = create_user()
    user.deactivate()

    with pytest.raises(UserAlreadyInactiveError):
        user.deactivate()


def test_activate_user():
    user = create_user()
    user.deactivate()

    user.activate()

    assert user.is_active is True


def test_activate_active_user_raises():
    user = create_user()

    with pytest.raises(UserAlreadyActiveError):
        user.activate()
