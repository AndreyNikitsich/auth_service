from datetime import timedelta
from typing import Annotated

from core.config.settings import settings
from db.fake import fake_users_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.tokens import Token
from schemas.users import BaseUser
from serrvices.tokens import create_access_token, get_current_active_user
from serrvices.users import UserManager

router = APIRouter(tags=["auth"])


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user_manager: Annotated[UserManager, Depends()]
) -> Token:
    user = user_manager.authenticate(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.token.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type=settings.token.token_type)


@router.get("/users/me/", response_model=BaseUser)
async def read_users_me(
        current_user: Annotated[BaseUser, Depends(get_current_active_user)]
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
        current_user: Annotated[BaseUser, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]
