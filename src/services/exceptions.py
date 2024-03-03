from enum import Enum


class ErrorCode(str, Enum):
    REGISTER_INVALID_PASSWORD = "REGISTER_INVALID_PASSWORD"  # noqa: S105
    REGISTER_USER_ALREADY_EXISTS = "REGISTER_USER_ALREADY_EXISTS"
    LOGIN_BAD_CREDENTIALS = "LOGIN_BAD_CREDENTIALS"
    NOT_VALIDATE_CREDENTIALS = "COULD NOT VALIDATE CREDENTIALS"
    INACTIVE_USER = "INACTIVE USER"

    INVALID_TOKEN_SIGNATURE = "INVALID_TOKEN_SIGNATURE"  # noqa: S105
    TOKEN_EXPIRED = "TOKEN_EXPIRED"  # noqa: S105
    REVOKED_REFRESH_TOKEN = "REVOKED_REFRESH_TOKEN"  # noqa: S105
    REVOKED_ACCESS_TOKEN = "REVOKED_ACCESS_TOKEN"  # noqa: S105
    INVALID_TOKEN_PAYLOAD = "INVALID_TOKEN_PAYLOAD"  # noqa: S105


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


class BaseTokenServiceError(Exception):
    code: ErrorCode


class InvalidTokenPayloadError(BaseTokenServiceError):
    code = ErrorCode.INVALID_TOKEN_PAYLOAD


class InvalidTokenSignatureError(BaseTokenServiceError):
    code = ErrorCode.INVALID_TOKEN_SIGNATURE


class ExpiredTokenError(BaseTokenServiceError):
    code = ErrorCode.TOKEN_EXPIRED


class AccessTokenServiceError(BaseTokenServiceError):
    pass


class RevokedAccessTokenError(AccessTokenServiceError):
    code = ErrorCode.REVOKED_ACCESS_TOKEN


class RefreshTokenServiceError(BaseTokenServiceError):
    pass


class RevokedRefreshTokenError(RefreshTokenServiceError):
    code = ErrorCode.REVOKED_REFRESH_TOKEN
