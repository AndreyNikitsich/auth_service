from typing import Annotated

from fastapi import APIRouter, Depends
from schemas.users import BaseUser, LoginHistory, UserLoginHistory
from services.tokens import get_current_active_user

router = APIRouter(tags=["users"], prefix="/users")


@router.get("/me", response_model=BaseUser)
async def read_users_me(
        current_user: Annotated[BaseUser, Depends(get_current_active_user)]
) -> BaseUser:
    return current_user


@router.get("/me/history")
async def read_users_login_history(
        current_user: Annotated[UserLoginHistory, Depends(get_current_active_user)]
) -> list[LoginHistory]:
    return current_user.login_histories
