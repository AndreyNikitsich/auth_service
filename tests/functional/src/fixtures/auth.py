import pytest_asyncio

from ...settings import test_settings


@pytest_asyncio.fixture(name="make_register")
def make_register(make_post_request):
    async def inner(email: str | None = None, password: str | None = None):
        url = test_settings.service_url + "/api/v1/auth/register"
        body, cookies, status = await make_post_request(url, body_data={"email": email, "password": password})
        return body, cookies, status

    return inner


@pytest_asyncio.fixture(name="make_login")
async def make_login(make_post_request):
    async def inner(email: str | None = None, password: str | None = None):
        url = test_settings.service_url + "/api/v1/auth/login"
        body, cookies, status = await make_post_request(url, body_data={"email": email, "password": password})
        return body, cookies, status

    return inner


@pytest_asyncio.fixture(name="make_logout")
async def make_logout(make_post_request):
    async def inner(access_token: str):
        url = test_settings.service_url + "/api/v1/auth/logout"
        body, cookies, status = await make_post_request(url, cookies={"access_token": access_token})
        return body, cookies, status

    return inner


@pytest_asyncio.fixture(name="make_logout_all")
async def make_logout_all(make_post_request):
    async def inner(access_token: str):
        url = test_settings.service_url + "/api/v1/auth/logout_all"
        body, cookies, status = await make_post_request(url, cookies={"access_token": access_token})
        return body, cookies, status

    return inner


@pytest_asyncio.fixture(name="make_refresh")
async def make_refresh(make_post_request):
    async def inner(refresh_token: str):
        url = test_settings.service_url + "/api/v1/auth/refresh"
        body, cookies, status = await make_post_request(url, cookies={"refresh_token": refresh_token})
        return body, cookies, status

    return inner


@pytest_asyncio.fixture(name="make_check_access")
async def make_check_access(make_post_request):
    async def inner(access_token: str):
        url = test_settings.service_url + "/api/v1/auth/check_access"
        body, cookies, status = await make_post_request(url, cookies={"access_token": access_token})
        return body, cookies, status

    return inner
