from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from dependensies.auth import get_access_token_service
from models.users import User
from services.exceptions import ErrorCode, UserNotExistsError
from services.tokens.access import AccessTokenService
from services.tokens.exceptions import BaseTokenServiceError
from services.users import UserManager, get_user_manager

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
