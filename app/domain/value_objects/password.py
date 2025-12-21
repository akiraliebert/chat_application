from app.domain.exceptions import WeakPasswordError


class Password:
    def __init__(self, hashed_value: str):
        if not hashed_value:
            raise WeakPasswordError("Password hash cannot be empty")
        self._hashed_value = hashed_value

    @property
    def value(self) -> str:
        return self._hashed_value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Password) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
