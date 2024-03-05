import pytest_asyncio

from ...settings import test_settings


@pytest_asyncio.fixture(name="get_me")
async def get_me(make_get_request):
    async def inner(access_token: str):
        url = test_settings.service_url + "/api/v1/users/me"
        body, cookies, status = await make_get_request(url, cookies={"access_token": access_token})
        return body, cookies, status

    return inner


@pytest_asyncio.fixture(name="get_login_history")
async def get_login_history(make_get_request):
    async def inner(access_token: str):
        url = test_settings.service_url + "/api/v1/users/me/history"
        body, cookies, status = await make_get_request(url, cookies={"access_token": access_token})
        return body, cookies, status

    return inner
