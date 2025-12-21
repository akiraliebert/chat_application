from app.domain.entities.user import User
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.repositories.user_repository import UserRepository

from app.application.uow.unit_of_work import UnitOfWork
from app.application.security.password_hasher import PasswordHasher
from app.application.exceptions import EmailAlreadyExistsError


class RegisterUserUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self._uow = uow
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, email: str, raw_password: str) -> User:
        async with self._uow:
            email_vo = Email(email)

            if await self._user_repository.exists_by_email(email_vo):
                raise EmailAlreadyExistsError()

            hashed_password = self._password_hasher.hash(raw_password)

            user = User(
                user_id=UserId(),
                email=email_vo,
                password=Password(hashed_password),
            )

            await self._user_repository.add(user)

            return user
