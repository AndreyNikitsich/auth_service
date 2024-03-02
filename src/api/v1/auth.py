from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from schemas.tokens import LoginOut
from schemas.users import BaseUser, UserCreate, UserCredentials
from services import exceptions
from services.auth import AuthService
from services.exceptions import BaseTokenServiceError, ErrorCode
from services.users import UserManager, get_user_manager

from ..dependencies import get_auth_service

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=BaseUser, status_code=status.HTTP_201_CREATED)
async def create_user(
        request: Request, user_create: UserCreate, user_manager: Annotated[UserManager, Depends(get_user_manager)]
) -> BaseUser:
    """Регистрация пользователя"""
    try:
        created_user = await user_manager.create(user_create)
    except exceptions.UserAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS)
    except exceptions.InvalidPasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_INVALID_PASSWORD,
        )

    return BaseUser.model_validate(created_user)


@router.post("/login")
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginOut:
    credentials = UserCredentials(username=form_data.username, password=form_data.password)
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.LOGIN_BAD_CREDENTIALS)

    refresh_token, access_token = await auth_service.login(user)
    await user_manager.on_after_login(user, request)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, path=request.url_for("refresh").path)
    response.set_cookie(key="access_token", value=access_token)

    return LoginOut(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(
    response: Response,
    access_token: Annotated[str, Cookie()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        await auth_service.logout(access_token)
    except BaseTokenServiceError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.code)

    response.status_code = status.HTTP_200_OK
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"detail": "OK"}


@router.post("/logout_all")
async def logout_all(
    response: Response,
    access_token: Annotated[str, Cookie()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        await auth_service.logout_all(access_token)
    except BaseTokenServiceError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.code)

    response.status_code = status.HTTP_200_OK
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"detail": "OK"}


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    refresh_token: Annotated[str, Cookie()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        new_refresh_token, new_access_token = await auth_service.refresh(refresh_token)
    except BaseTokenServiceError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.code)

    response.status_code = status.HTTP_200_OK
    response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, path=request.url.path)
    response.set_cookie(key="access_token", value=new_access_token)

    return LoginOut(refresh_token=new_refresh_token, access_token=new_access_token)


@router.post("/check_access")
async def check_access(
    response: Response,
    access_token: Annotated[str, Cookie()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        await auth_service.check_access(access_token)
    except BaseTokenServiceError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.code)

    response.status_code = status.HTTP_200_OK

    return {"detail": "OK"}
