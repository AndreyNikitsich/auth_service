from typing import Any

import aiohttp
import pytest_asyncio


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request():
    async def inner(url: str, query_data: dict[str, Any] | None = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=query_data) as response:
                body = await response.json()
                headers = response.headers
                status = response.status

        return body, headers, status

    return inner
