import pytest
from datetime import timezone

from app.domain.entities.user import User
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password


@pytest.mark.asyncio
async def test_add_and_get_user_by_id(user_repository, uow):
    user = User(
        user_id=UserId(),
        email=Email("integration@test.com"),
        password=Password("hashed-password"),
    )

    async with uow:
        await user_repository.add(user)

    found = await user_repository.get_by_id(user.id)

    assert found is not None
    assert found.id == user.id
    assert found.email == user.email
    assert found.password == user.password
    assert found.is_active is True
    assert found.created_at.tzinfo == timezone.utc


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, uow):
    user = User(
        user_id=UserId(),
        email=Email("email@test.com"),
        password=Password("hashed-password"),
    )

    async with uow:
        await user_repository.add(user)

    found = await user_repository.get_by_email(Email("email@test.com"))

    assert found is not None
    assert found.id == user.id


@pytest.mark.asyncio
async def test_exists_by_email(user_repository, uow):
    email = Email("exists@test.com")

    user = User(
        user_id=UserId(),
        email=email,
        password=Password("hashed-password"),
    )

    async with uow:
        await user_repository.add(user)

    exists = await user_repository.exists_by_email(email)

    assert exists is True


@pytest.mark.asyncio
async def test_user_not_found(user_repository):
    result = await user_repository.get_by_email(
        Email("missing@test.com")
    )

    assert result is None
