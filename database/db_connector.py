import psycopg
from psycopg import Connection
import os
from dotenv import load_dotenv
import logging

from __main__ import config


def create_connection() -> Connection:
    """
    create a database connection to a Postgres database

    :return: connection object
    """

    connection = psycopg.connect(
        dbname=config.database_schema_name,
        user=config.database_user,
        password=config.database_password,
        host=config.database_host,
        port=config.database_port,
    )
    if connection:
        return connection
    else:
        raise Exception("Database connection failed")
