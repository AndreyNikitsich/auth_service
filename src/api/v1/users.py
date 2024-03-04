from typing import Annotated

from fastapi import APIRouter, Depends

from schemas.users import BaseUser, LoginHistory, UserLoginHistory

from ..dependencies import get_current_active_user, get_user_or_404

router = APIRouter(tags=["users"], prefix="/users")


@router.get("/me", response_model=BaseUser)
async def read_users_me(current_user: Annotated[BaseUser, Depends(get_current_active_user)]) -> BaseUser:
    return current_user


@router.get("/me/history", response_model=BaseUser)
async def read_users_login_history(
    current_user: Annotated[UserLoginHistory, Depends(get_current_active_user)],
) -> list[LoginHistory]:
    return current_user.login_histories


@router.get("/{id}", response_model=BaseUser)
async def get_user(user: Annotated[BaseUser, Depends(get_user_or_404)]):
    return user
