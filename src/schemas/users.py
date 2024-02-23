from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str
    email: str | None = None
    is_active: bool | None = None


class UserInDB(BaseUser):
    hashed_password: str
