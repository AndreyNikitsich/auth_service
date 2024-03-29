from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from passlib import pwd
from passlib.context import CryptContext

from db.users import UserDatabase, get_user_db
from models.users import LoginHistory, User
from schemas.users import CreateLoginHistory, UserCredentials, UserUpdate
from services import exceptions


class PasswordHelper:
    def __init__(self):
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_and_update(self, plain_password: str, hashed_password: str) -> tuple[bool, str | None]:
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
        """Get user by id in database."""
        user = await self.user_db.get(user_id)
        if user is None:
            raise exceptions.UserNotExistsError()

        return user

    async def get_users(self, page_size: int | None, page_number: int | None) -> list[User]:
        """Get users in database."""
        return await self.user_db.all(
            limit=page_size, offset=self._get_offset(page_number=page_number, page_size=page_size)
        )

    async def create(self, user_create: UserCredentials, is_superuser: bool = False) -> User:
        """Create a user in database."""
        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExistsError()

        user_dict = user_create.model_dump(exclude_unset=True)

        user_dict["is_superuser"] = is_superuser

        user_role = "superuser" if is_superuser else "guest"
        user_dict["role"] = user_role

        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        return created_user

    async def update(self, user_update: UserUpdate, user: User) -> User:
        """Update a user in database."""
        user_dict = user_update.model_dump(exclude_unset=True)
        updated_user = await self.user_db.update(user, user_dict)

        return updated_user

    async def delete(self, user: User) -> None:
        """Delete a user in database."""
        await self.user_db.delete(user)

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

    async def get_login_history(
        self, user_id: UUID, page_size: int | None, page_number: int | None
    ) -> list[LoginHistory]:
        """Get user login history."""
        return await self.user_db.get_login_history(
            user_id=user_id, limit=page_size, offset=self._get_offset(page_number=page_number, page_size=page_size)
        )

    async def on_after_login(self, user: User, request: Request) -> None:
        """Logic after user login."""
        history = CreateLoginHistory(
            user_id=user.id,
            useragent=request.headers.get("user-agent", ""),
            referer=request.headers.get("referer", ""),
            remote_addr=request.client.host if request.client else "",
        )
        await self.user_db.add_login_history(user, history.model_dump())

    @staticmethod
    def _get_offset(page_number: int | None, page_size: int | None) -> int | None:
        if page_number is not None and page_size is not None:
            return (page_number - 1) * page_size

        return None


async def get_user_manager(user_db: Annotated[UserDatabase, Depends(get_user_db)]):
    yield UserManager(user_db)
