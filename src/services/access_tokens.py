import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import jwt
from pydantic import ValidationError

from entities.tokens import AccessToken
from repositories.refresh_tokens.redis_revoked_refresh_token import RedisRevokedRefreshTokenRepository

from .base_tokens import BaseTokenService
from .exceptions import InvalidTokenPayloadError, RevokedAccessTokenError


@dataclass
class AccessTokenService(BaseTokenService):
    revoked_refresh_repo: RedisRevokedRefreshTokenRepository

    async def generate_token(self, user_id: str, refresh_jti: str, **kwargs) -> str:
        issued_at = datetime.now(timezone.utc)
        expire = issued_at + timedelta(minutes=self.expires_delta_minutes)

        to_encode = {
            "jti": str(uuid.uuid4()),
            "refresh_jti": refresh_jti,
            "sub": user_id,
            "iat": issued_at,
            "exp": expire,
            **kwargs,
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def validate_token(self, encoded_token: str) -> AccessToken:
        await super().validate_token(encoded_token)

        payload = self.get_payload(encoded_token)

        if await self.revoked_refresh_repo.exist(payload.refresh_jti):
            raise RevokedAccessTokenError

        return payload

    def get_payload(self, encoded_token: str) -> AccessToken:
        try:
            return AccessToken(**jwt.get_unverified_claims(encoded_token))
        except ValidationError as e:
            raise InvalidTokenPayloadError from e
