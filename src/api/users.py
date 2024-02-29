from typing import Annotated

from fastapi import APIRouter, Depends
from schemas.users import BaseUser
from services.tokens import get_current_active_user

router = APIRouter(tags=["users"], prefix="/users")


@router.get("/me", response_model=BaseUser)
async def read_users_me(
        current_user: Annotated[BaseUser, Depends(get_current_active_user)]
) -> BaseUser:
    return current_user


@router.get("/me/history")
async def read_own_items(
        current_user: Annotated[BaseUser, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]
