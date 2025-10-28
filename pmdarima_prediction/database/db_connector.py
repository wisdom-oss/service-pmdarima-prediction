import psycopg
from psycopg import Connection
from psycopg.rows import TupleRow

from .. import config

__connection: Connection[TupleRow] | None = None


def create_connection() -> Connection:
    """
    create a database connection to a Postgres database

    :return: connection object
    """
    global __connection

    if __connection is None or __connection.closed:
        __connection = psycopg.connect(
            dbname=config.db_name,
            user=config.db_user,
            password=config.db_password.get_secret_value(),
            host=config.db_host,
            port=config.db_port,
        )

    return __connection
