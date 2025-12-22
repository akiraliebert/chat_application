from passlib.context import CryptContext

from app.application.security.password_hasher import PasswordHasher


_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class BCryptPasswordHasher(PasswordHasher):
    def hash(self, raw_password: str) -> str:
        return _pwd_context.hash(raw_password)

    def verify(self, raw_password: str, hashed_password: str) -> bool:
        return _pwd_context.verify(raw_password, hashed_password)
