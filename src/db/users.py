from typing import Annotated, Any, Type
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Executable

from db.postgres import get_session
from models.users import LoginHistory, User


class UserDatabase:
    def __init__(self, session: AsyncSession, user_model: Type[User]):
        self.session = session
        self.user_model = user_model
        self.history_model = LoginHistory

    async def all(self, limit: int | None, offset: int | None) -> list[User]:
        statement = select(self.user_model).limit(limit).offset(offset).order_by(self.user_model.created_at)
        results = await self.session.execute(statement)
        return list(results.scalars())

    async def get(self, id: str) -> User | None:
        statement = select(self.user_model).where(self.user_model.id == id)
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(self.user_model).where(func.lower(self.user_model.email) == email.lower())
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

    async def add_login_history(self, user: User, history_dict: dict[str, Any]) -> None:
        login_history = LoginHistory(**history_dict)
        self.session.add(login_history)
        await self.session.commit()
        await self.session.refresh(user)
        await self.session.refresh(login_history)

    async def _get_user(self, statement: Executable) -> User | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def get_login_history(self, user_id: UUID, limit: int | None, offset: int | None) -> list[LoginHistory]:
        statement = select(self.history_model).where(self.history_model.user_id == user_id).limit(limit).offset(offset)
        results = await self.session.execute(statement)
        return list(results.scalars())


async def get_user_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield UserDatabase(session, User)
