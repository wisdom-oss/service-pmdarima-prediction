import psycopg
import os
from dotenv import load_dotenv


def create_connection():
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
        return connection
    except Exception as error:
        print(error)


