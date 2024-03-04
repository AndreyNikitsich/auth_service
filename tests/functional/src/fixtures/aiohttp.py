from typing import Any

import aiohttp
import pytest_asyncio


@pytest_asyncio.fixture(name="make_post_request")
def make_post_request():
    async def inner(url: str, body_data: dict[str, Any] | None = None, cookies: dict | None = None) -> Any:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body_data, cookies=cookies) as response:
                body = await response.json()
                cookies = response.cookies
                status = response.status

        return body, cookies, status

    return inner


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request():
    async def inner(url: str, cookies: dict | None = None) -> Any:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, cookies=cookies) as response:
                body = await response.json()
                cookies = response.cookies
                status = response.status

        return body, cookies, status

    return inner
