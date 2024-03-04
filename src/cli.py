import contextlib
from functools import wraps
from typing import Annotated

import anyio
import typer
from pydantic import ValidationError
from rich import print
from rich.console import Console

from db.postgres import get_session
from db.users import get_user_db
from schemas.users import UserCredentials
from services.exceptions import UserAlreadyExistsError
from services.users import get_user_manager

err_console = Console(stderr=True)

get_async_session_context = contextlib.asynccontextmanager(get_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


def run_async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        async def coro_wrapper():
            return await func(*args, **kwargs)

        return anyio.run(coro_wrapper)

    return wrapper


async def create_user(credentials: UserCredentials, is_superuser: bool = False):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(credentials, is_superuser=is_superuser)
                    print(f"[bold green]User created {user}[/bold green]")
    except UserAlreadyExistsError:
        print(f"[bold red]User {credentials.email} already exists[/bold red]")
        raise typer.Abort()


@run_async
async def main(email: Annotated[str, typer.Option()], password: Annotated[str, typer.Option()]):
    try:
        credentials = UserCredentials(email=email, password=password)
        await create_user(credentials, True)
    except ValidationError as exc:
        for error in exc.errors():
            err_console.log(repr(error["msg"]))
        raise typer.Abort()


if __name__ == "__main__":
    typer.run(main)
