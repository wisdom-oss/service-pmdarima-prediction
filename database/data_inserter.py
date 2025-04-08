import os

from dotenv import load_dotenv
from database import db_con, file_reader

def create_table():
    """
    create the database table
    :return: None
    """
    load_dotenv()
    table_string = os.getenv("TABLE_STRING")

    with db_con.create_connection() as connection:
        with connection.cursor() as cursor:
            # execute creation
            cursor.execute(table_string)
            print("Table created!")

def create_hypertable():
    """
    create a hypertable from the main table, to fasten searching
    :return: none
    """
    with db_con.create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT create_hypertable('timeseries.water_demand_prediction', by_range('date'));")
            print("Hypertable initialized!")

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

    with db_con.create_connection() as connection:
        with connection.cursor() as cursor:
            # iterate through every row in df
            for row in df.itertuples(name=None):
                # ignore index row[0]
                cursor.execute(insert_string, (row[1], row[2], row[3]))
                print(f"Row {row[0] + 1}_{row[1]}_{row[2]}_{row[3]} inserted!")

create_table()
create_hypertable()
insert_data()