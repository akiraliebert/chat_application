from app.application.uow.unit_of_work import UnitOfWork
from app.application.security.password_hasher import PasswordHasher
from app.application.exceptions import InvalidCredentialsError, InactiveUserError


from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.email import Email


class LoginUserUseCase:
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

            user = await self._user_repository.get_by_email(email_vo)
            if user is None:
                raise InvalidCredentialsError()

            if not user.is_active:
                raise InactiveUserError()

            if not self._password_hasher.verify(raw_password, user.password.value):
                raise InvalidCredentialsError()

            return user
