import dataclasses
from abc import ABC, abstractmethod
from typing import Any

from entities.tokens import RefreshToken


@dataclasses.dataclass
class BaseRefreshTokenRepository(ABC):
    client: Any

    @abstractmethod
    async def save(self, refresh_token: RefreshToken) -> None:
        ...

    @abstractmethod
    async def delete(self, jti: str) -> None:
        ...

    @abstractmethod
    async def exist(self, jti: str) -> bool:
        ...

    @abstractmethod
    async def delete_by_user_id(self, user_id: str) -> list[str]:
        ...


@dataclasses.dataclass
class BaseRevokedRefreshTokenRepository(ABC):
    client: Any

    @abstractmethod
    async def save(self, jti: str) -> None:
        ...

    @abstractmethod
    async def bulk_save(self, jti_list: list[str]) -> None:
        ...

    @abstractmethod
    async def exist(self, jti: str) -> bool:
        ...
