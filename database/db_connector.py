import psycopg
from psycopg import Connection
import os
from dotenv import load_dotenv
import logging


def create_connection() -> Connection | None:
    """
    create a database connection to a Postgres database
    
    :return: connection object
    """
    try:
        load_dotenv()

        database = os.getenv("DB")
        username = os.getenv("USER")
        password = os.getenv("PW")

        print(password)

        host = os.getenv("HOST")
        port = os.getenv("PORT")


        if database == None:
            raise Exception("no database name set up")
        
        if username == None or password == None:
            raise Exception("Database Credentials Missing")
        

        connection = psycopg.connect(dbname=database.strip(),
                                      user=username.strip(),
                                      password=password.strip(),
                                      host=host.strip(),
                                      port=port.strip())
        if connection:
            logging.debug(f"Database connection established")
            return connection
        else:
            logging.error(f"Database connection failed")
    except Exception as error:
        logging.debug(f"Connection not established, because of {error}")
        raise Exception(f"Database connection failed")


