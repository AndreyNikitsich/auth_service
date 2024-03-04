import psycopg2
import pytest_asyncio

from ...settings import test_settings


@pytest_asyncio.fixture
def clear_db():
    with psycopg2.connect(test_settings.db_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE login_histories, users, refresh_tokens CASCADE")
