from typing import Annotated, Any, Type

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Executable

from db.postgres import get_session
from models.users import Role


class RoleDatabase:
    def __init__(self, session: AsyncSession, role_model: Type[Role]):
        self.session = session
        self.role_model = role_model

    async def all(self):
        statement = select(self.role_model)
        results = await self.session.execute(statement)
        return list(results.scalars())

    async def get(self, id: str) -> Role | None:
        statement = select(self.role_model).where(self.role_model.id == id)
        return await self._get_role(statement)

    async def get_by_title(self, title: str) -> Role | None:
        statement = select(self.role_model).where(func.lower(self.role_model.title) == title.lower())
        return await self._get_role(statement)

    async def _get_role(self, statement: Executable) -> Role | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def create(self, role_create: dict[str, Any]) -> Role:
        role = self.role_model(**role_create)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def update(self, role: Role, update_dict: dict[str, Any]) -> Role:
        for key, value in update_dict.items():
            setattr(role, key, value)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def delete(self, role: Role) -> None:
        await self.session.delete(role)
        await self.session.commit()


async def get_role_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield RoleDatabase(session, Role)
