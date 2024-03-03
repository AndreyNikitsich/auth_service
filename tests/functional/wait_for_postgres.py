import time

import psycopg2

from settings import test_settings

if __name__ == "__main__":
    while True:
        try:
            with psycopg2.connect(test_settings) as conn:
                break
        except (psycopg2.DatabaseError, Exception):
            print("Could not connect to postgres")
            time.sleep(1)
