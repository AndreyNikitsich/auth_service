from functools import wraps
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.postgres import get_session
from db.redis_db import get_redis
from models.users import User
from repositories.refresh_tokens.redis_revoked_refresh_token import RedisRevokedRefreshTokenRepository
from repositories.refresh_tokens.sqlalchemy_refresh_token import SQLAlchemyRefreshTokenRepository
from schemas.auth_request import AuthRequest
from schemas.users import BaseUser, PaginationParams
from services.access_tokens import AccessTokenService
from services.auth import AuthService
from services.exceptions import BaseTokenServiceError, ErrorCode, UserNotExistsError
from services.refresh_tokens import RefreshTokenService
from services.users import UserManager, get_user_manager
from settings import settings


def roles_required(roles_list: list[str]):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user: BaseUser = kwargs.get("request").custom_user  # type: ignore
            if not user or user.role not in roles_list:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            return await function(*args, **kwargs)

        return wrapper

    return decorator


def get_revoked_refresh_tokens_repo(
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> RedisRevokedRefreshTokenRepository:
    return RedisRevokedRefreshTokenRepository(client=redis_client)


def get_refresh_tokens_repo(
    db_client: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemyRefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(client=db_client)


def get_refresh_token_service(
    refresh_token_repo: Annotated[SQLAlchemyRefreshTokenRepository, Depends(get_refresh_tokens_repo)],
    revoked_refresh_tokens_repo: Annotated[
        RedisRevokedRefreshTokenRepository, Depends(get_revoked_refresh_tokens_repo)
    ],
) -> RefreshTokenService:
    return RefreshTokenService(
        secret_key=settings.token.secret_key,
        public_key=settings.token.public_key,
        algorithm=settings.token.algorithm,
        expires_delta_minutes=settings.token.refresh_token_expire_minutes,
        repo=refresh_token_repo,
        revoked_repo=revoked_refresh_tokens_repo,
    )


def get_access_token_service(
    revoked_refresh_repo: Annotated[RedisRevokedRefreshTokenRepository, Depends(get_revoked_refresh_tokens_repo)],
) -> AccessTokenService:
    return AccessTokenService(
        secret_key=settings.token.secret_key,
        public_key=settings.token.public_key,
        algorithm=settings.token.algorithm,
        expires_delta_minutes=settings.token.access_token_expire_minutes,
        revoked_refresh_repo=revoked_refresh_repo,
    )


def get_auth_service(
    access_token_service: Annotated[AccessTokenService, Depends(get_access_token_service)],
    refresh_token_service: Annotated[RefreshTokenService, Depends(get_refresh_token_service)],
    user_service: Annotated[UserManager, Depends(get_user_manager)],
):
    return AuthService(
        access_token_service=access_token_service,
        refresh_token_service=refresh_token_service,
        user_service=user_service,
    )


async def get_current_user(
    access_token: Annotated[str, Cookie()],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    access_token_service: Annotated[AccessTokenService, Depends(get_access_token_service)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ErrorCode.NOT_VALIDATE_CREDENTIALS,
    )

    try:
        payload = await access_token_service.validate_token(access_token)
    except BaseTokenServiceError:
        raise credentials_exception

    try:
        user = await user_manager.get_user(user_id=payload.sub)
    except UserNotExistsError:
        raise credentials_exception

    return user


async def get_current_user_global(request: AuthRequest, user: Annotated[BaseUser, Depends(get_current_user)]):
    request.custom_user = user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.INACTIVE_USER)
    return current_user


async def get_current_superuser(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.IS_NOT_SUPERUSER)
    return current_user


def get_pagination_params(
    page_number: int = Query(settings.api.default_page_number, gt=0),
    page_size: int = Query(settings.api.default_page_size, gt=0),
) -> PaginationParams:
    return PaginationParams(page_number=page_number, page_size=page_size)
