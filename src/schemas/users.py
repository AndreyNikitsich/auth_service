from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints


class UserRoles(BaseModel):
    title: str

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class BaseUser(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    roles: list[Annotated[str, StringConstraints(max_length=255)]]

    model_config = ConfigDict(from_attributes=True)


class LoginHistory(BaseModel):
    login_date: datetime = Field(..., validation_alias="created_at")
    useragent: str
    remote_addr: str
    referer: str

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class UserLoginHistory(BaseUser):
    login_histories: list[LoginHistory]


class UserCredentials(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=20)


class UserCreate(UserCredentials):
    roles: list[Annotated[str, StringConstraints(max_length=255)]] = Field(default=["guest"])


class UserUpdate(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    roles: list[Annotated[str, StringConstraints(max_length=255)]]

    model_config = ConfigDict(from_attributes=True)


class CreateLoginHistory(BaseModel):
    user_id: UUID
    useragent: str | None = None
    referer: str | None = None
    remote_addr: str | None = None


class PaginationParams(BaseModel):
    page_number: int | None
    page_size: int | None
