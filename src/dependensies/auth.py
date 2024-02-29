from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.settings import settings
from db.postgres import get_session
from db.redis_db import get_redis
from repositories.refresh_tokens.base import BaseRefreshTokenRepository, BaseRevokedRefreshTokenRepository
from repositories.refresh_tokens.redis_revoked_refresh_token import RedisRevokedRefreshTokenRepository
from repositories.refresh_tokens.sqlalchemy_refresh_token import SQLAlchemyRefreshTokenRepository
from services.auth import AuthService
from services.tokens.access import AccessTokenService
from services.tokens.refresh import RefreshTokenService
from services.users import UserManager, get_user_manager


def get_revoked_refresh_tokens_repo(
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> BaseRevokedRefreshTokenRepository:
    return RedisRevokedRefreshTokenRepository(client=redis_client)


def get_refresh_tokens_repo(db_client: Annotated[AsyncSession, Depends(get_session)]) -> BaseRefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(client=db_client)


def get_refresh_token_service(
    refresh_token_repo: Annotated[BaseRefreshTokenRepository, Depends(get_refresh_tokens_repo)],
    revoked_refresh_tokens_repo: Annotated[BaseRevokedRefreshTokenRepository, Depends(get_revoked_refresh_tokens_repo)],
) -> RefreshTokenService:
    return RefreshTokenService(
        secret_key=settings.token.secret_key,
        algorithm=settings.token.algorithm,
        expires_delta_minutes=settings.token.refresh_token_expire_minutes,
        repo=refresh_token_repo,
        revoked_repo=revoked_refresh_tokens_repo,
    )


def get_access_token_service(
    revoked_refresh_repo: Annotated[BaseRevokedRefreshTokenRepository, Depends(get_revoked_refresh_tokens_repo)],
) -> AccessTokenService:
    return AccessTokenService(
        secret_key=settings.token.secret_key,
        algorithm=settings.token.algorithm,
        expires_delta_minutes=settings.token.refresh_token_expire_minutes,
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
