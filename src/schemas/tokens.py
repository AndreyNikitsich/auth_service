from pydantic import BaseModel

from settings import settings


class LoginOut(BaseModel):
    access_token: str
    refresh_token: str
    type: str = settings.token.type
