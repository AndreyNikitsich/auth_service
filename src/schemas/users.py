from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class BaseUser(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserInDB(BaseUser):
    hashed_password: str


class UserCredentials(BaseModel):
    username: str
    password: str
