from typing import Annotated, Any, Type

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Executable

from db.postgres import get_session
from models.users import User


class UserDatabase:
    def __init__(self, session: AsyncSession, user_model: Type[User]):
        self.session = session
        self.user_model = user_model

    async def get(self, id: str) -> User | None:
        statement = select(self.user_model).where(self.user_model.id == id)
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(self.user_model).where(func.lower(self.user_model.email) == email.lower())
        return await self._get_user(statement)

    async def get_by_username(self, username: str) -> User | None:
        statement = select(self.user_model).where(func.lower(self.user_model.username) == username.lower())
        return await self._get_user(statement)

    async def create(self, user_create: dict[str, Any]) -> User:
        user = self.user_model(**user_create)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, update_dict: dict[str, Any]) -> User:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def _get_user(self, statement: Executable) -> User | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()


async def get_user_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield UserDatabase(session, User)
