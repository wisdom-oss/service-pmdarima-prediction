import psycopg
import os
from dotenv import load_dotenv
import logging


def create_connection() -> psycopg.connection or None:
    """
    create a database connection to a Postgres database
    :return: connection object
    """
    try:
        load_dotenv()
        connection = psycopg.connect(dbname=os.getenv("DB"),
                                      user=os.getenv("USER"),
                                      password=os.getenv("PW"),
                                      host=os.getenv("HOST"),
                                      port=os.getenv("PORT"))
        if connection:
            logging.debug(f"Database connection established")
        return connection
    except Exception as error:
        logging.debug(error)
        return None


