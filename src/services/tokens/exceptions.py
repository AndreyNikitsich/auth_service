from enum import Enum


class ErrorCodes(str, Enum):
    INVALID_TOKEN_SIGNATURE = "INVALID_TOKEN_SIGNATURE"  # noqa: S105
    TOKEN_EXPIRED = "TOKEN_EXPIRED"  # noqa: S105
    REVOKED_REFRESH_TOKEN = "REVOKED_REFRESH_TOKEN"  # noqa: S105
    REVOKED_ACCESS_TOKEN = "REVOKED_ACCESS_TOKEN"  # noqa: S105
    INVALID_TOKEN_PAYLOAD = "INVALID_TOKEN_PAYLOAD"  # noqa: S105


class BaseTokenServiceError(Exception):
    code: ErrorCodes


class InvalidTokenPayloadError(BaseTokenServiceError):
    code = ErrorCodes.INVALID_TOKEN_PAYLOAD


class InvalidTokenSignatureError(BaseTokenServiceError):
    code = ErrorCodes.INVALID_TOKEN_SIGNATURE


class ExpiredTokenError(BaseTokenServiceError):
    code = ErrorCodes.TOKEN_EXPIRED


class AccessTokenServiceError(BaseTokenServiceError):
    pass


class RevokedAccessTokenError(AccessTokenServiceError):
    code = ErrorCodes.REVOKED_ACCESS_TOKEN


class RefreshTokenServiceError(BaseTokenServiceError):
    pass


class RevokedRefreshTokenError(RefreshTokenServiceError):
    code = ErrorCodes.REVOKED_REFRESH_TOKEN
