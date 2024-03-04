import time

import psycopg2

from settings import test_settings

if __name__ == "__main__":
    while True:
        try:
            with psycopg2.connect(test_settings.db_dsn) as conn:
                break
        except (psycopg2.DatabaseError, Exception):
            time.sleep(1)
