class DomainError(Exception):
    pass


class InvalidEmailError(DomainError):
    pass


class WeakPasswordError(DomainError):
    pass


class UserAlreadyActiveError(DomainError):
    pass


class UserAlreadyInactiveError(DomainError):
    pass


class InvalidRoomNameError(DomainError):
    pass


class UserNotInRoomError(DomainError):
    pass


class UserAlreadyInRoomError(DomainError):
    pass
