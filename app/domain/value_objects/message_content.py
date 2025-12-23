from app.domain.exceptions import InvalidMessageContentError


class MessageContent:
    def __init__(self, value: str):
        value = value.strip()
        if not value:
            raise InvalidMessageContentError("Message cannot be empty")
        if len(value) > 4000:
            raise InvalidMessageContentError("Message is too long")

        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MessageContent) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
