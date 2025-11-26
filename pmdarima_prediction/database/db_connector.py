from sqlalchemy import URL, Connection, Engine, create_engine

from .. import config

__connection: Engine | None = None


def get_engine() -> Engine:
    global __connection

    if __connection is None:
        __url = URL.create(
            drivername="postgresql",
            username=config.db_user,
            password=config.db_password.get_secret_value(),
            host=config.db_host,
            database=config.db_name,
        )
        __connection = create_engine(__url)

    return __connection


def create_connection() -> Connection:
    """
    create a database connection to a Postgres database

    :return: connection object
    """
    global __connection

    if __connection is None:
        __url = URL.create(
            drivername="postgresql",
            username=config.db_user,
            password=config.db_password.get_secret_value(),
            host=config.db_host,
            database=config.db_name,
        )
        __connection = create_engine(__url)

    return __connection.connect()
