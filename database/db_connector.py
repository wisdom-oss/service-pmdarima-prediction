import psycopg
from psycopg import Connection
import os
from dotenv import load_dotenv
import logging

from __main__ import config

from psycopg.rows import TupleRow

__connection: Connection[TupleRow] | None = None

def create_connection() -> Connection:
    """
    create a database connection to a Postgres database

    :return: connection object
    """
    global __connection

    if __connection is None or __connection.closed:

        __connection = psycopg.connect(
            dbname=config.database_schema_name,
            user=config.database_user,
            password=config.database_password,
            host=config.database_host,
            port=config.database_port,
        )

    return __connection
