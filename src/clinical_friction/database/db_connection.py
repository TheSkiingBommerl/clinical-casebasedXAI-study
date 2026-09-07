from pathlib import Path
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import execute_values
from loguru import logger
from psycopg2.extensions import connection

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)
#print(env_path)

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def close_exception(err: BaseException):
    """Close the db connection if an exception occurs"""
    if isinstance(err, psycopg2.Error):
        cur = err.cursor
        conn = cur.connection
        cur.close()
        conn.close()
        logger.warning("Closed database connection")

@logger.catch(reraise=True, onerror=close_exception)
def db_conn() -> connection:

    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

@logger.catch(reraise=True, onerror=close_exception)
def store_data(query, data):

    conn = db_conn()
    cur = conn.cursor()

    execute_values(cur, query, data)

    conn.commit()
    cur.close()
    conn.close()

@logger.catch(reraise=True, onerror=close_exception)
def extract_data(query, info=None):

    conn = db_conn()
    cur = conn.cursor()

    if info is None:
        cur.execute(query)
    else:
        cur.execute(query, info)

    rows = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    return rows

@logger.catch(reraise=True, onerror=close_exception)
def extract_data_efficiently(query, info=None, chunk_size=50):
    conn = db_conn()
    cur = conn.cursor(name="streaming_cursor")
    cur.itersize = chunk_size

    if info is None:
        cur.execute(query)
    else:
        cur.execute(query, tuple(info) if info is not None else info)

    yield from cur

    cur.close()
    conn.close()
