import pytest

from app.application.use_cases.user.register_user import RegisterUserUseCase
from app.application.exceptions import EmailAlreadyExistsError

from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password


@pytest.fixture
def use_case(uow, user_repository, password_hasher):
    return RegisterUserUseCase(
        uow=uow,
        user_repository=user_repository,
        password_hasher=password_hasher,
    )


@pytest.mark.asyncio
async def test_register_user_success(use_case, user_repository, uow):
    user = await use_case.execute(
        email="test@example.com",
        raw_password="plain-password",
    )

    assert isinstance(user, User)
    assert user.email == Email("test@example.com")
    assert user.password == Password("hashed-password")

    user_repository.exists_by_email.assert_awaited_once()
    user_repository.add.assert_awaited_once()

    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_register_user_email_already_exists(use_case, user_repository, uow):
    user_repository.exists_by_email.return_value = True

    with pytest.raises(EmailAlreadyExistsError):
        await use_case.execute(
            email="test@example.com",
            raw_password="plain-password",
        )

    user_repository.add.assert_not_called()
    assert uow.committed is False
    assert uow.rolled_back is True


@pytest.mark.asyncio
async def test_password_is_hashed_before_user_creation(use_case, password_hasher):
    await use_case.execute(
        email="test@example.com",
        raw_password="plain-password",
    )

    password_hasher.hash.assert_called_once_with("plain-password")
