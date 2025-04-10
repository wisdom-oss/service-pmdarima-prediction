import os

from dotenv import load_dotenv
from database import db_connector

def request_date_value(meter_name: str, start: int, end: int) -> list or None:
    """
    request data from db
    :param meter_name: name of smartmeter
    :param start: unix time of first record
    :param end: unix time of last record
    :return: list or None of results
    """
    load_dotenv()
    query_string = os.getenv("SEARCH_STRING_NAME_START_END")

    with db_connector.create_connection() as connection:
        with connection.cursor() as cursor:
            query = query_string
            cursor.execute(query, (meter_name, start, end))
            return cursor.fetchall()