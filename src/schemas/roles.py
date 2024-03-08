from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoleCreate(BaseModel):
    title: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(RoleCreate):
    pass


class BaseRole(RoleCreate):
    id: UUID
