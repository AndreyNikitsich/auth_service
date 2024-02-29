from datetime import datetime

from pydantic import BaseModel


class JWTToken(BaseModel):
    encoded_token: str | None = None
    jti: str
    sub: str
    iat: datetime
    exp: datetime


class RefreshToken(JWTToken):
    pass


class AccessToken(JWTToken):
    refresh_jti: str

    is_superuser: bool | None
    is_verified: bool | None
    is_active: bool | None