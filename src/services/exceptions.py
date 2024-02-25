from enum import Enum


class ErrorCode(str, Enum):
    REGISTER_INVALID_PASSWORD = "REGISTER_INVALID_PASSWORD"  # noqa: S105
    REGISTER_USER_ALREADY_EXISTS = "REGISTER_USER_ALREADY_EXISTS"
    LOGIN_BAD_CREDENTIALS = "LOGIN_BAD_CREDENTIALS"
    NOT_VALIDATE_CREDENTIALS = "COULD NOT VALIDATE CREDENTIALS"
    INACTIVE_USER = "INACTIVE USER"


class UsersError(Exception):
    pass


class UserAlreadyExistsError(UsersError):
    pass


class UserNotExistsError(UsersError):
    pass


class UserInactiveError(UsersError):
    pass


class InvalidPasswordError(UsersError):
    pass
