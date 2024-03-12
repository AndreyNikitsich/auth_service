from fastapi import Request

from schemas.users import BaseUser


class AuthRequest(Request):
    custom_user: BaseUser
