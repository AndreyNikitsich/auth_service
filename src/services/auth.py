import dataclasses

from models.users import User
from .access_tokens import AccessTokenService
from .refresh_tokens import RefreshTokenService
from .users import UserManager


@dataclasses.dataclass
class AuthService:
    access_token_service: AccessTokenService
    refresh_token_service: RefreshTokenService
    user_service: UserManager

    async def login(self, user: User):
        refresh_token = await self.refresh_token_service.generate_token(str(user.id))
        refresh_payload = self.refresh_token_service.get_payload(refresh_token)
        access_token = await self.access_token_service.generate_token(
            str(user.id),
            refresh_payload.jti,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
        )

        return refresh_token, access_token

    async def refresh(self, refresh_token: str):
        payload = await self.refresh_token_service.validate_token(refresh_token)
        await self.refresh_token_service.revoke_token(payload.jti)

        user = await self.user_service.get_user(payload.sub)
        return await self.login(user)

    async def check_access(self, access_token: str):
        await self.access_token_service.validate_token(access_token)

    async def logout(self, access_token: str):
        payload = await self.access_token_service.validate_token(access_token)
        await self.refresh_token_service.revoke_token(payload.refresh_jti)

    async def logout_all(self, access_token: str):
        payload = await self.access_token_service.validate_token(access_token)
        await self.refresh_token_service.revoke_user_tokens(payload.sub)
