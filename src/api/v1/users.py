from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from models.users import User, UserRoles
from schemas.auth_request import AuthRequest
from schemas.users import BaseUser, LoginHistory, PaginationParams, UserLoginHistory, UserUpdate
from services.exceptions import UserNotExistsError
from services.users import UserManager, get_user_manager

from ..dependencies import get_current_active_user, get_current_user_global, get_pagination_params, roles_required

router = APIRouter(tags=["users"], prefix="/users", dependencies=[Depends(get_current_user_global)])

user_roles = UserRoles()


async def get_user_or_404(
    id: str,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
) -> User:
    try:
        return await user_manager.get_user(id)
    except UserNotExistsError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


@router.get(
    "/",
    response_model=list[BaseUser],
    name="list_users",
    summary="Получение списка пользователей",
    status_code=status.HTTP_200_OK,
)
@roles_required(roles_list=[user_roles.admin, user_roles.superuser])
async def get_users(
    request: AuthRequest,
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
) -> list[BaseUser]:
    results = await user_manager.get_users(page_size=pagination.page_size, page_number=pagination.page_number)
    return [BaseUser.model_validate(result) for result in results]


@router.get(
    "/me",
    name="user_me",
    summary="Получение личных данных пользователя",
    response_model=BaseUser,
    status_code=status.HTTP_200_OK,
)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> BaseUser:
    return BaseUser.model_validate(current_user)


@router.get(
    "/me/history",
    name="user_me_history",
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
    name="user",
    summary="Получение данных пользователя",
    response_model=BaseUser,
    status_code=status.HTTP_200_OK,
)
@roles_required(roles_list=[user_roles.admin, user_roles.superuser])
async def get_user(request: AuthRequest, user: Annotated[User, Depends(get_user_or_404)]):
    return BaseUser.model_validate(user)


@router.patch(
    "/{id}",
    name="patch_user",
    response_model=BaseUser,
    summary="Изменение данных пользователя",
    status_code=status.HTTP_200_OK,
)
@roles_required(roles_list=[user_roles.admin, user_roles.superuser])
async def update_role(
    request: AuthRequest,
    user_update: UserUpdate,
    user: Annotated[User, Depends(get_user_or_404)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
) -> BaseUser:
    updated_user = await user_manager.update(user_update, user)
    return BaseUser.model_validate(updated_user)
