import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import jwt
from pydantic import ValidationError

from entities.tokens import RefreshToken
from repositories.refresh_tokens.base import BaseRevokedRefreshTokenRepository
from repositories.refresh_tokens.sqlalchemy_refresh_token import BaseRefreshTokenRepository

from .base import BaseTokenService
from .exceptions import InvalidTokenPayloadError, RevokedRefreshTokenError


@dataclass
class RefreshTokenService(BaseTokenService):
    repo: BaseRefreshTokenRepository
    revoked_repo: BaseRevokedRefreshTokenRepository

    async def generate_token(self, user_id: str) -> str:
        issued_at = datetime.now(timezone.utc)
        expire = issued_at + timedelta(minutes=self.expires_delta_minutes)

        payload = RefreshToken(
            jti=str(uuid.uuid4()),
            sub=user_id,
            iat=issued_at,
            exp=expire,
        )

        encoded_jwt = jwt.encode(payload.model_dump(), self.secret_key, algorithm=self.algorithm)
        await self.repo.save(payload)

        return encoded_jwt

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
