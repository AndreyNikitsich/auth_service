import dataclasses

from services.tokens.access import AccessTokenService
from services.tokens.refresh import RefreshTokenService


@dataclasses.dataclass
class AuthService:
    access_token_service: AccessTokenService
    refresh_token_service: RefreshTokenService

    async def login(self, user_id: str):
        refresh_token = await self.refresh_token_service.generate_token(user_id)
        refresh_payload = self.refresh_token_service.get_payload(refresh_token)
        access_token = await self.access_token_service.generate_token(user_id, refresh_payload.jti)

        return refresh_token, access_token

    async def refresh(self, refresh_token: str):
        payload = await self.refresh_token_service.validate_token(refresh_token)
        await self.refresh_token_service.revoke_token(payload.jti)
        return await self.login(payload.sub)

    async def check_access(self, access_token: str):
        await self.access_token_service.validate_token(access_token)

    async def logout(self, access_token: str):
        payload = await self.access_token_service.validate_token(access_token)
        await self.refresh_token_service.revoke_token(payload.refresh_jti)

    async def logout_all(self, access_token: str):
        payload = await self.access_token_service.validate_token(access_token)
        await self.refresh_token_service.revoke_user_tokens(payload.sub)
