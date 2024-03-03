from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BaseUser(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class LoginHistory(BaseModel):
    login_date: datetime = Field(..., validation_alias="created_at")
    useragent: str
    remote_addr: str
    referer: str

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class UserLoginHistory(BaseUser):
    login_histories: list[LoginHistory]


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserInDB(BaseUser):
    hashed_password: str


class UserCredentials(BaseModel):
    username: str
    password: str


class CreateLoginHistory(BaseModel):
    user_id: UUID
    useragent: str
    referer: str
    remote_addr: str
