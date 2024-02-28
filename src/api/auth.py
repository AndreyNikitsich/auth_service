from datetime import timedelta
from typing import Annotated

from core.config.settings import settings
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.tokens import Token
from schemas.users import BaseUser, UserCreate, UserCredentials
from services import exceptions
from services.exceptions import ErrorCode
from services.tokens import create_access_token
from services.users import UserManager, get_user_manager

router = APIRouter(tags=["auth"])


@router.post(
    "/register",
    response_model=BaseUser,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
        user_create: UserCreate,
        user_manager: Annotated[UserManager, Depends(get_user_manager)]
) -> BaseUser:
    """Регистрация пользователя"""
    try:
        created_user = await user_manager.create(user_create)
    except exceptions.UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS
        )
    except exceptions.InvalidPasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_INVALID_PASSWORD,
        )

    return BaseUser.model_validate(created_user)


@router.post("/login")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_manager: Annotated[UserManager, Depends(get_user_manager)]
) -> Token:
    credentials = UserCredentials(username=form_data.username, password=form_data.password)
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS
        )

    access_token_expires = timedelta(
        minutes=settings.token.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type=settings.token.token_type)
