from typing import Annotated

from fastapi import APIRouter, Depends, status

from schemas.users import BaseUser, LoginHistory, PaginationParams, UserLoginHistory
from services.users import UserManager, get_user_manager

from ..dependencies import get_current_active_user, get_pagination_params, get_user_or_404

router = APIRouter(tags=["users"], prefix="/users")


@router.get(
    "/me",
    summary="Получение личных данных пользователя",
    response_model=BaseUser,
    status_code=status.HTTP_200_OK,
)
async def read_users_me(current_user: Annotated[BaseUser, Depends(get_current_active_user)]) -> BaseUser:
    return current_user


@router.get(
    "/me/history",
    summary="Получение пользователем своей истории входов в аккаунт",
    response_model=list[LoginHistory],
    status_code=status.HTTP_200_OK,
)
async def read_users_login_history(
    current_user: Annotated[UserLoginHistory, Depends(get_current_active_user)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
) -> list[LoginHistory]:
    results = await user_manager.get_login_history(
        user_id=current_user.id, page_size=pagination.page_size, page_number=pagination.page_number
    )
    return [LoginHistory.model_validate(result) for result in results]


@router.get("/{id}", response_model=BaseUser)
async def get_user(user: Annotated[BaseUser, Depends(get_user_or_404)]):
    return user
