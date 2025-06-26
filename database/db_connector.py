import psycopg
import os
from dotenv import load_dotenv
import logging


def create_connection() -> psycopg.connection:
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
        else:
            logging.error(f"Database connection failed")
    except Exception as error:
        logging.debug(f"Connection not established, because of {error}")
        raise Exception(f"Database connection failed")


