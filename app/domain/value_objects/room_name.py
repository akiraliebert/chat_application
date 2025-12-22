from app.domain.exceptions import InvalidRoomNameError


class RoomName:
    def __init__(self, value: str):
        value = value.strip()
        if not value:
            raise InvalidRoomNameError("Room name cannot be empty")
        if len(value) > 100:
            raise InvalidRoomNameError("Room name is too long")

        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RoomName) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
