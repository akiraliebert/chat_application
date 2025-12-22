import pytest

from app.application.use_cases.user.login_user import (
    LoginUserUseCase,
    InvalidCredentialsError,
    InactiveUserError,
)



@pytest.fixture
def use_case(uow, user_repository, password_hasher):
    return LoginUserUseCase(
        uow=uow,
        user_repository=user_repository,
        password_hasher=password_hasher,
    )


@pytest.mark.asyncio
async def test_login_success(
    uow,
    use_case,
    user_repository,
    password_hasher,
    active_user,
):
    user_repository.get_by_email.return_value = active_user

    result = await use_case.execute(
        email="test@example.com",
        raw_password="plain-password",
    )

    assert result == active_user
    assert uow.committed is True
    assert uow.rolled_back is False

    password_hasher.verify.assert_called_once_with(
        "plain-password",
        active_user.password.value,
    )


@pytest.mark.asyncio
async def test_login_user_not_found(
    uow,
    use_case,
    user_repository,
    password_hasher,
):
    user_repository.get_by_email.return_value = None

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(
            email="test@example.com",
            raw_password="plain-password",
        )

    assert uow.committed is False
    assert uow.rolled_back is True


@pytest.mark.asyncio
async def test_login_inactive_user(
    uow,
    use_case,
    user_repository,
    password_hasher,
    inactive_user,
):
    user_repository.get_by_email.return_value = inactive_user

    with pytest.raises(InactiveUserError):
        await use_case.execute(
            email="test@example.com",
            raw_password="plain-password",
        )

    assert uow.committed is False
    assert uow.rolled_back is True


@pytest.mark.asyncio
async def test_login_invalid_password(
    uow,
    use_case,
    user_repository,
    password_hasher,
    active_user,
):
    user_repository.get_by_email.return_value = active_user
    password_hasher.verify.return_value = False

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(
            email="test@example.com",
            raw_password="wrong-password",
        )

    assert uow.committed is False
    assert uow.rolled_back is True
