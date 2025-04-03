import psycopg2
import os
import file_reader

from dotenv import load_dotenv


def create_connection():
    load_dotenv()
    connection = psycopg2.connect(database=os.getenv("DB"),
                                  user=os.getenv("USER"),
                                  password=os.getenv("PW"),
                                  host=os.getenv("HOST"),
                                  port=os.getenv("PORT"))

    return connection


def create_table():
    try:
        # open connection
        connection = create_connection()
        cursor = connection.cursor()

        # load table create string
        load_dotenv()
        table_string = os.getenv("TABLE_STRING")

        # execute creation
        cursor.execute(table_string)
        connection.commit()

        print("Table created successfully!")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()
        connection.close()


def insert_data():

    # read in whole json data
    df = file_reader.format_smartmeter_data()

    # get insert string
    load_dotenv()
    insert_string = os.getenv("INSERT_STRING")

    try:
        connection = create_connection()
        cursor = connection.cursor()

        # iterate through every row in df
        for row in df.itertuples(name=None):
            cursor.execute(insert_string, (row[1], row[2], row[3]))
            print(f"Row {row[0]+1}_{row[1]}_{row[2]}_{row[3]} inserted!")

        # commit after whole json is read in
        connection.commit()
    except Exception as e:
        print(f"Error in {row[0]+1}: {e}")
    finally:
        cursor.close()
        connection.close()



