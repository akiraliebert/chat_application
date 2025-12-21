import re
from app.domain.exceptions import InvalidEmailError


_EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


class Email:
    def __init__(self, value: str):
        value = value.lower().strip()
        if not _EMAIL_RE.match(value):
            raise InvalidEmailError(f"Invalid email: {value}")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Email) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)