import logging
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from environment / .env file")

_pool = pool.ThreadedConnectionPool(minconn=2, maxconn=10, dsn=DATABASE_URL)


def get_conn():
    return _pool.getconn()


def db_execute(
    query: str,
    params=None,
    fetch: bool = False,
    fetchall: bool = False,
    return_rowcount: bool = False,
):
   
    conn   = _pool.getconn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(query, params or ())

        result = None
        if fetchall:
            result = cursor.fetchall()
        elif fetch:
            result = cursor.fetchone()
        elif return_rowcount:
            result = cursor.rowcount

        conn.commit()
        return result

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        _pool.putconn(conn)