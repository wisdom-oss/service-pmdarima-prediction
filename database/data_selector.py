import datetime

import psycopg
from dotenv import load_dotenv

import interfaces
from database import db_connector
from psycopg.rows import dict_row


def query_fetch_one(query_string: str, params: list[str | datetime.datetime]) -> interfaces.FetchOneQueryDict | None:
    """
    fetch one function to use when querying data
    :param query_string: select string to use
    :param params: lst of parameters
    :return: dict of results or None if None
    """
    with db_connector.create_connection() as connection:
        with connection.cursor(row_factory=psycopg.rows.dict_row) as cursor:
            query = query_string
            cursor.execute(query, (tuple(params)))
            result = cursor.fetchone()
            return result

def select_date_value(meter_name: str, start: datetime.datetime, end: datetime.datetime) -> interfaces.SelectDateValueData | None:
    """
    request data from db
    
    :param meter_name: name of smartmeter
    :param start: unix time of first record
    :param end: unix time of last record
    :return: dict or None of results
    """
    load_dotenv()
    query_string = "SELECT array_agg(value ORDER BY date) AS value, array_agg(date ORDER by date) AS date FROM timeseries.water_demand_prediction WHERE name=%s AND date BETWEEN %s AND %s"

    return query_fetch_one(query_string, [meter_name, start, end])

def select_names() -> dict[str: list[str]] | None:
    """
    request names of data from db, based on first timestamp (currently)
    
    :return: dict of names
    """
    search_date = "2021-05-26 00:00:00"
    search_string = "SELECT array_agg(name ORDER BY date) as names FROM timeseries.water_demand_prediction WHERE date=%s"
    return query_fetch_one(search_string, [search_date])

