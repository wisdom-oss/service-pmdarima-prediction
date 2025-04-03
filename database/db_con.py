import psycopg2
import os
from dotenv import load_dotenv
from database import file_reader


def create_connection():
    """
    create a database connection to the postgres database
    :return: connection object
    """
    load_dotenv()

    connection = psycopg2.connect(database=os.getenv("DB"),
                                  user=os.getenv("USER"),
                                  password=os.getenv("PW"),
                                  host=os.getenv("HOST"),
                                  port=os.getenv("PORT"))

    return connection


def create_table():
    """
    create the database table
    :return: None
    """
    # load table create string
    load_dotenv()
    table_string = os.getenv("TABLE_STRING")

    with create_connection() as connection:
        with connection.cursor() as cursor:
            # execute creation
            cursor.execute(table_string)
            connection.commit()

            print("Table created successfully!")


def insert_data():
    """
    insert data based on files in smartmeterdata
    :return: None
    """

    # read in whole json data
    df = file_reader.format_smartmeter_data()

    # get insert string
    load_dotenv()
    insert_string = os.getenv("INSERT_STRING")

    with create_connection() as connection:
        with connection.cursor() as cursor:

            # iterate through every row in df
            for row in df.itertuples(name=None):
                # ignore index row[0]
                cursor.execute(insert_string, (row[1], row[2], row[3], row[4]))
                print(f"Row {row[0] + 1}_{row[1]}_{row[2]}_{row[3]} inserted!")


def request_value_unix_time(meter_name: str, start: int, end: int) -> list or None:
    """
    request data from db
    :param meter_name: name of smartmeter
    :param start: unix time of first record
    :param end: unix time of last record
    :return: list or None of results
    """
    load_dotenv()
    query_string = os.getenv("SEARCH_STRING_NAME_START_END")

    with create_connection() as connection:
        with connection.cursor() as cursor:
            query = query_string
            cursor.execute(query, (meter_name, start, end))
            return cursor.fetchall()

