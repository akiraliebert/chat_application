class ApplicationError(Exception):
    pass


class EmailAlreadyExistsError(ApplicationError):
    pass


class InvalidCredentialsError(ApplicationError):
    pass


class InactiveUserError(ApplicationError):
    pass


class RoomAlreadyExistsError(ApplicationError):
    pass


class RoomNotFoundError(ApplicationError):
    pass


class UserAlreadyInRoomError(ApplicationError):
    pass


class SecondUserIsRequired(ApplicationError):
    pass
