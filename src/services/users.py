from typing import Annotated

from fastapi import Depends, Request
from passlib import pwd
from passlib.context import CryptContext

from db.users import UserDatabase, get_user_db
from models.users import User
from schemas.users import CreateLoginHistory, UserCredentials
from services import exceptions


class PasswordHelper:
    def __init__(self):
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_and_update(
            self, plain_password: str, hashed_password: str
    ) -> tuple[bool, str | None]:
        return self.context.verify_and_update(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        return self.context.hash(password)

    @staticmethod
    def generate() -> str:
        return pwd.genword()


class UserManager:
    def __init__(self, user_db: UserDatabase):
        self.user_db = user_db
        self.password_helper = PasswordHelper()

    async def get_user(self, user_id: str) -> User:
        user = await self.user_db.get(user_id)
        if user is None:
            raise exceptions.UserNotExistsError()

        return user

    async def create(self, user_create: UserCredentials) -> User:
        """Create a user in database."""
        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExistsError()

        user_dict = user_create.model_dump(
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
            },
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        return created_user

    async def authenticate(self, credentials: UserCredentials) -> User | None:
        """
        Authenticate and return a user following an email and a password.
        Will automatically upgrade password hash if necessary.
        """
        try:
            user = await self.get_by_email(credentials.email)
        except exceptions.UserNotExistsError:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )

        if not verified:
            return None

        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user

    async def get_by_email(self, user_email: str) -> User:
        """Get a user by e-mail."""
        user = await self.user_db.get_by_email(user_email)

        if user is None:
            raise exceptions.UserNotExistsError()

        return user

    async def on_after_login(self, user: User, request: Request) -> None:
        """Logic after user login."""
        history = CreateLoginHistory(
            user_id=user.id,
            useragent=request.headers.get("user-agent"),
            referer=request.headers.get("referer"),
            remote_addr=request.client.host if request.client else None
        )
        await self.user_db.add_login_history(user, history.model_dump())


async def get_user_manager(user_db: Annotated[UserDatabase, Depends(get_user_db)]):
    yield UserManager(user_db)
