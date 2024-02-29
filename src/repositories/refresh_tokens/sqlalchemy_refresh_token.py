import dataclasses

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from entities.tokens import RefreshToken
from models.refresh_tokens import RefreshToken as RefreshTokenModel

from .base import BaseRefreshTokenRepository


@dataclasses.dataclass
class SQLAlchemyRefreshTokenRepository(BaseRefreshTokenRepository):
    client: AsyncSession

    async def save(self, token: RefreshToken):
        db_token = RefreshTokenModel(
            id=token.jti,
            user_id=token.sub,
            issued_at=token.iat,
            expires_at=token.exp,
            is_revoked=False,
        )
        self.client.add(db_token)
        await self.client.commit()

    async def delete(self, jti: str):
        stmt = update(RefreshTokenModel).where(RefreshTokenModel.id == jti).values(is_revoked=True)
        await self.client.execute(stmt)
        await self.client.commit()

    async def exist(self, jti: str) -> bool:
        stmt = select(func.count()).where((RefreshTokenModel.id == jti) & (RefreshTokenModel.is_revoked is False))
        result = await self.client.execute(stmt)
        count = result.scalar_one()
        return count > 0

    async def delete_by_user_id(self, user_id: str) -> list[str]:
        stmt = (
            update(RefreshTokenModel)
            .where((RefreshTokenModel.user_id == user_id) & (RefreshTokenModel.is_revoked is False))
            .values(is_revoked=True)
            .returning(RefreshTokenModel.id)
        )
        result = await self.client.execute(stmt)
        ids = [str(i[0]) for i in result.all()]
        await self.client.commit()
        return ids
