from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_register_flow(make_register, clear_db):
    user_email = "test@test.com"
    user_password = "password"

    body, _, status = await make_register(user_email, user_password)

    assert status == HTTPStatus.CREATED
    assert body["email"] == user_email
    assert body["is_active"] is True
    assert body["is_superuser"] is False
    assert body["is_verified"] is False


@pytest.mark.asyncio
async def test_login_flow(make_register, make_login, clear_db):
    user_email = "test3@test.com"
    user_password = "password"

    await make_register(user_email, user_password)
    body, _, status = await make_login(user_email, user_password)

    assert status == HTTPStatus.OK
    assert body.get("access_token") is not None
    assert body.get("refresh_token") is not None


@pytest.mark.asyncio
async def test_refresh_flow(make_register, make_login, make_refresh, clear_db):
    user_email = "test@test.com"
    user_password = "password"

    await make_register(user_email, user_password)
    body, _, _ = await make_login(user_email, user_password)
    refresh_token = body.get("refresh_token")

    body, _, status = await make_refresh(refresh_token)

    assert status == HTTPStatus.OK
    assert body.get("access_token") is not None
    assert body.get("refresh_token") is not None


@pytest.mark.asyncio
async def test_logout_flow(make_register, make_login, make_logout, clear_db):
    user_email = "test@test.com"
    user_password = "password"

    await make_register(user_email, user_password)
    body, _, _ = await make_login(user_email, user_password)

    access_token = body["access_token"]

    body, _, status = await make_logout(access_token)
    assert status == HTTPStatus.OK


@pytest.mark.asyncio
async def test_logout_all_flow(make_register, make_login, make_logout_all, make_check_access, clear_db):
    user_email = "test@test.com"
    user_password = "password"

    await make_register(user_email, user_password)

    access_tokens = []
    for _ in range(2):
        body, _, _ = await make_login(user_email, user_password)
        access_token = body.get("access_token")
        access_tokens.append(access_token)

    _, cookies, status = await make_logout_all(access_tokens[0])
    assert status == HTTPStatus.OK

    body, _, status = await make_check_access(access_tokens[1])
    assert status == HTTPStatus.FORBIDDEN
    assert body.get("detail") == "REVOKED_ACCESS_TOKEN"
