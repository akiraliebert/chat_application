from uuid import UUID, uuid4


class RoomId:
    def __init__(self, value: UUID | None = None):
        self._value = value or uuid4()

    @property
    def value(self) -> UUID:
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RoomId) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
