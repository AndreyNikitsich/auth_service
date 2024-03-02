from dataclasses import dataclass

from jose import jwt
from pydantic import ValidationError

from entities.tokens import RefreshToken
from repositories.refresh_tokens.redis_revoked_refresh_token import RedisRevokedRefreshTokenRepository
from repositories.refresh_tokens.sqlalchemy_refresh_token import SQLAlchemyRefreshTokenRepository

from .base_tokens import BaseTokenService
from .exceptions import InvalidTokenPayloadError, RevokedRefreshTokenError


@dataclass
class RefreshTokenService(BaseTokenService):
    repo: SQLAlchemyRefreshTokenRepository
    revoked_repo: RedisRevokedRefreshTokenRepository

    async def generate_token(self, user_id: str) -> str:
        to_encode = {"sub": user_id}
        encoded_token = self._generate_token(to_encode)
        payload = self.get_payload(encoded_token)
        await self.repo.save(payload)
        return encoded_token

    async def validate_token(self, encoded_token: str) -> RefreshToken:
        await super().validate_token(encoded_token)

        payload = self.get_payload(encoded_token)

        if not await self.repo.exist(payload.jti):
            raise RevokedRefreshTokenError

        return payload

    async def revoke_token(self, token_jti: str):
        await self.repo.delete(token_jti)
        await self.revoked_repo.save(token_jti)

    async def revoke_user_tokens(self, user_id: str):
        deleted_token_ids = await self.repo.delete_by_user_id(user_id=user_id)
        await self.revoked_repo.bulk_save(deleted_token_ids)

    def get_payload(self, encoded_token: str) -> RefreshToken:
        try:
            return RefreshToken(**jwt.get_unverified_claims(encoded_token))
        except ValidationError as e:
            raise InvalidTokenPayloadError from e
