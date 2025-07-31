import logging
import sys

from database import db_connector, file_reader

# logger setup
logging.basicConfig(
    # Capture Inserting Process
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def create_table() -> None:
    """
    create the database table
    :return: None
    """

    table_string = (f"CREATE TABLE IF NOT EXISTS timeseries.water_demand_prediction (date TIMESTAMPTZ NOT NULL, "
                    f"name TEXT NOT NULL, value DOUBLE PRECISION NOT NULL, PRIMARY KEY (date, name, value));")

    with db_connector.create_connection() as connection:
        with connection.cursor() as cursor:
            # execute creation
            cursor.execute(table_string)
            logging.debug("Table created!")

def create_hypertable() ->  None:
    """
    create a hypertable from the main table, to fasten searching
    :return: none
    """
    with db_connector.create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT create_hypertable('timeseries.water_demand_prediction', by_range('date'));")
            logging.debug("Hypertable initialized!")

def insert_data() -> None:
    """
    insert data based on files in smartmeterdata
    :return: None
    """

    # read in whole json data
    df = file_reader.format_smartmeter_data()

    insert_string = f"INSERT INTO timeseries.water_demand_prediction (date, name, value) VALUES (%s, %s, %s)"

    with db_connector.create_connection() as connection:
        with connection.cursor() as cursor:
            # iterate through every row in df
            for row in df.itertuples(name=None):
                # ignore index row[0]
                cursor.execute(insert_string, (row[1], row[2], row[3]))
                logging.debug(f"Row {row[0] + 1}_{row[1]}_{row[2]}_{row[3]} inserted!")

#create_table()
#create_hypertable()
#insert_data()