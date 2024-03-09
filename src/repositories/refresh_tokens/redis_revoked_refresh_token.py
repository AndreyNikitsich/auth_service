import dataclasses

from redis.asyncio import Redis

from settings import settings


@dataclasses.dataclass
class RedisRevokedRefreshTokenRepository:
    client: Redis
    key_prefix = "revoked_refresh_token_"
    ttl = settings.token.access_token_expire_minutes * 60

    async def save(self, jti: str):
        # we need refresh jti in redis only while related to it access token is alive
        await self.client.set(self.key_prefix + jti, "", self.ttl)

    async def bulk_save(self, jti_list: list[str]) -> None:
        pipe = await self.client.pipeline()
        for jti in jti_list:
            pipe.set(self.key_prefix + jti, "", self.ttl)
        await pipe.execute(True)

    async def exist(self, jti: str):
        value = await self.client.get(self.key_prefix + jti)
        return value is not None
