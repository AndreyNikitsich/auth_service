from typing import Annotated

from fastapi import Depends

from db.roles import RoleDatabase, get_role_db
from models.users import Role
from schemas.roles import RoleCreate, RoleUpdate
from services import exceptions


class RoleManager:
    def __init__(self, role_db: RoleDatabase):
        self.role_db = role_db

    async def get_role(self, role_id: str) -> Role:
        """Get role by id in database."""
        role = await self.role_db.get(role_id)
        if role is None:
            raise exceptions.RoleNotExistsError()

        return role

    async def create(self, role_create: RoleCreate) -> Role:
        existing_role = await self.role_db.get_by_title(role_create.title)
        if existing_role is not None:
            raise exceptions.RoleAlreadyExistsError()
        role_dict = role_create.model_dump(exclude_unset=True)
        created_role = await self.role_db.create(role_dict)

        return created_role

    async def update(self, role_update: RoleUpdate, role: Role) -> Role:
        role_dict = role_update.model_dump(exclude_unset=True)
        updated_role = await self.role_db.update(role, role_dict)

        return updated_role

    async def delete(self, role: Role) -> None:
        await self.role_db.delete(role)

    async def get_roles(self):
        return await self.role_db.all()


async def get_role_manager(role_db: Annotated[RoleDatabase, Depends(get_role_db)]):
    yield RoleManager(role_db)
