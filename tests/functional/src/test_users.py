import pytest


@pytest.mark.asyncio
async def test_users_me(make_register, make_login, get_me, clear_db):
    user_email = "test@test.com"
    user_password = "123"

    _, _, _ = await make_register(user_email, user_password)
    body, _, _ = await make_login(user_email, user_password)
    access_token = body["access_token"]
    body, _, _ = await get_me(access_token)

    assert user_email == body["email"]


@pytest.mark.asyncio
async def test_users_login_history(make_register, make_login, get_login_history, clear_db):
    user_email = "test@test.com"
    user_password = "123"

    _, _, _ = await make_register(user_email, user_password)

    login_count = 3
    for _ in range(login_count):
        body, _, _ = await make_login(user_email, user_password)
        access_token = body["access_token"]

    body, _, _ = await get_login_history(access_token)
    assert len(body) == login_count
