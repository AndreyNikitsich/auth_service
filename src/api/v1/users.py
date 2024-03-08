from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from models.users import User
from schemas.users import BaseUser, LoginHistory, PaginationParams, UserLoginHistory
from services.exceptions import UserNotExistsError
from services.users import UserManager, get_user_manager

from ..dependencies import get_current_active_user, get_current_superuser, get_pagination_params

router = APIRouter(tags=["users"], prefix="/users")


async def get_user_or_404(
    id: str,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
) -> User:
    try:
        return await user_manager.get_user(id)
    except UserNotExistsError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


@router.get(
    "/me",
    summary="Получение личных данных пользователя",
    response_model=BaseUser,
    status_code=status.HTTP_200_OK,
)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> BaseUser:
    return BaseUser.model_validate(current_user)


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


@router.get(
    "/{id}",
    summary="Получение данных пользователя",
    response_model=BaseUser,
    dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)
async def get_user(user: Annotated[User, Depends(get_user_or_404)]):
    return BaseUser.model_validate(user)
