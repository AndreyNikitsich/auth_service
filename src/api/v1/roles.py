from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from api.dependencies import get_current_user_global, roles_required
from api.v1.users import user_roles
from models.roles import Role
from schemas.auth_request import AuthRequest
from schemas.roles import BaseRole, RoleCreate, RoleUpdate
from services.exceptions import RoleNotExistsError
from services.roles import RoleManager, get_role_manager

router = APIRouter(tags=["roles"], prefix="/roles", dependencies=[Depends(get_current_user_global)])


async def get_role_or_404(id: str, role_manager: Annotated[RoleManager, Depends(get_role_manager)]) -> Role:
    try:
        return await role_manager.get_role(id)
    except RoleNotExistsError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


@router.post(
    "/",
    response_model=BaseRole,
    name="create_roles",
    summary="Создание роли",
    status_code=status.HTTP_201_CREATED,
)
@roles_required(roles_list=[user_roles.admin, user_roles.superuser])
async def create_role(
    request: AuthRequest, role_create: RoleCreate, role_manager: Annotated[RoleManager, Depends(get_role_manager)]
) -> BaseRole:
    role = await role_manager.create(role_create)
    return BaseRole.model_validate(role)


@router.get(
    "/",
    response_model=list[BaseRole],
    name="list_roles",
    summary="Список ролей",
    status_code=status.HTTP_200_OK,
)
@roles_required(roles_list=[user_roles.admin, user_roles.superuser])
async def get_roles(
    request: AuthRequest, role_manager: Annotated[RoleManager, Depends(get_role_manager)]
) -> list[BaseRole]:
    results = await role_manager.get_roles()
    return [BaseRole.model_validate(result) for result in results]


@router.get(
    "/{id}",
    response_model=BaseRole,
    name="role",
    summary="Получение роли",
    status_code=status.HTTP_200_OK,
)
@roles_required(roles_list=[user_roles.admin, user_roles.superuser])
async def get_role(request: AuthRequest, role: Annotated[Role, Depends(get_role_or_404)]) -> BaseRole:
    return BaseRole.model_validate(role)


@router.patch(
    "/{id}",
    response_model=BaseRole,
    name="patch_role",
    summary="Изменение роли",
    status_code=status.HTTP_200_OK,
)
@roles_required(roles_list=[user_roles.admin, user_roles.superuser])
async def update_role(
    request: AuthRequest,
    role_update: RoleUpdate,
    role: Annotated[Role, Depends(get_role_or_404)],
    role_manager: Annotated[RoleManager, Depends(get_role_manager)],
) -> BaseRole:
    updated_role = await role_manager.update(role_update, role)
    return BaseRole.model_validate(updated_role)


@router.delete(
    "/{id}",
    response_class=Response,
    name="delete_role",
    summary="Удаление роли",
    status_code=status.HTTP_204_NO_CONTENT,
)
@roles_required(roles_list=[user_roles.admin, user_roles.superuser])
async def delete_role(
    request: AuthRequest,
    role: Annotated[Role, Depends(get_role_or_404)],
    role_manager: Annotated[RoleManager, Depends(get_role_manager)],
):
    await role_manager.delete(role)
    return None
