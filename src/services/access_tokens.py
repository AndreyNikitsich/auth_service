from dataclasses import dataclass

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
        to_encode = {
            "sub": user_id,
            "refresh_jti": refresh_jti,
            **kwargs,
        }
        return self._generate_token(to_encode)

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
