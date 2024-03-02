from typing import Annotated

from fastapi import APIRouter, Depends

from ..dependencies import get_current_active_user
from schemas.users import BaseUser

router = APIRouter(tags=["users"])


@router.get("/users/me/", response_model=BaseUser)
async def read_users_me(current_user: Annotated[BaseUser, Depends(get_current_active_user)]) -> BaseUser:
    return current_user


@router.get("/users/me/items/")
async def read_own_items(current_user: Annotated[BaseUser, Depends(get_current_active_user)]):
    return [{"item_id": "Foo", "owner": current_user.username}]
