from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.users import User
from settings import settings
from db.postgres import get_session
from db.redis_db import get_redis
from repositories.refresh_tokens.redis_revoked_refresh_token import RedisRevokedRefreshTokenRepository
from repositories.refresh_tokens.sqlalchemy_refresh_token import SQLAlchemyRefreshTokenRepository
from services.access_tokens import AccessTokenService
from services.auth import AuthService

from services.exceptions import ErrorCode, BaseTokenServiceError, UserNotExistsError
from services.refresh_tokens import RefreshTokenService
from services.users import UserManager, get_user_manager


def get_revoked_refresh_tokens_repo(
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> RedisRevokedRefreshTokenRepository:
    return RedisRevokedRefreshTokenRepository(client=redis_client)


def get_refresh_tokens_repo(db_client: Annotated[AsyncSession, Depends(get_session)]) -> SQLAlchemyRefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(client=db_client)


def get_refresh_token_service(
    refresh_token_repo: Annotated[SQLAlchemyRefreshTokenRepository, Depends(get_refresh_tokens_repo)],
    revoked_refresh_tokens_repo: Annotated[RedisRevokedRefreshTokenRepository, Depends(get_revoked_refresh_tokens_repo)],
) -> RefreshTokenService:
    return RefreshTokenService(
        secret_key=settings.token.secret_key,
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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    access_token_service: Annotated[AccessTokenService, Depends(get_access_token_service)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ErrorCode.NOT_VALIDATE_CREDENTIALS,
    )

    try:
        payload = await access_token_service.validate_token(token)
    except BaseTokenServiceError:
        raise credentials_exception

    try:
        user = await user_manager.get_user(user_id=payload.sub)
    except UserNotExistsError:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.INACTIVE_USER)
    return current_user
