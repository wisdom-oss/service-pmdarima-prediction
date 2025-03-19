import requests
from pandas import json_normalize, to_datetime
from datetime import datetime, timedelta
import pandas as pd
import logging

def request_weather_info(labels: list) -> pd.DataFrame:
    start, end = __convert_timestamps(labels[0], labels[-1])

    #capability, column_name = "air_temperature", "TT_TU"
    capability, column_name = "precipitation", "R1"

    try:
        response = requests.get(
            f"https://wisdom-demo.uol.de/api/dwd/00691/{capability}/hourly?from={start}&until={end}"
        )

        logging.debug("successfully requested weather info")

    except Exception as e:
        error_type = type(e).__name__
        logging.debug(f"Request to Weather-API failed. \n {error_type}: {e}")

    data = response.json()

    # Transform into DataFrame
    df = json_normalize(data["timeseries"])

    df = adjust_timestamp_column(df, "ts")

    df = fill_missing_timestamps(df)

    logging.debug(f"{df.head()}")

    return df[[column_name]]


def __convert_timestamps(start, end) -> tuple[int, int]:

    if not isinstance(start, datetime) and not isinstance(end, datetime):
        format_string = "%d.%m.%y %H:%M"

        datetime_start = datetime.strptime(start, format_string)
        datetime_end = datetime.strptime(end, format_string)
    else:
        datetime_start = start
        datetime_end = end

    # Convert to Unix timestamp
    unix_start = int(datetime_start.timestamp())
    unix_end = int(datetime_end.timestamp())

    return unix_start, unix_end


def adjust_timestamp_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    # Convert the timestamp column to datetime,
    # ensuring the format is correctly interpreted 2021-10-27T22:00:00Z
    df[column_name] = to_datetime(df[column_name], format="%Y-%m-%dT%H:%M:%SZ")

    # Adjust by 2 hours
    df[column_name] = df[column_name] + timedelta(hours=2)

    # Optionally, convert back to the original format if needed
    df[column_name] = df[column_name].dt.strftime("%d.%m.%y %H:%M")

    return df


def fill_missing_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    creates a new date range for the df in order to check up on missing timestamps
    :param df: the original df with requested weather data
    :return: the full content df with no missing timestamps
    """

    try:
        # Ensure the 'timestamp' column is in datetime format
        df['timestamp'] = pd.to_datetime(df['ts'], format='%d.%m.%y %H:%M')

        # Create a date range from the first to the last timestamp in the DataFrame
        start_timestamp = df['timestamp'].min()
        end_timestamp = df['timestamp'].max()
        all_timestamps = pd.date_range(start=start_timestamp, end=end_timestamp, freq='h')

        # Create a DataFrame with the complete range of timestamps
        all_timestamps_df = pd.DataFrame(all_timestamps, columns=['timestamp'])

        # Merge the new date range with the original DataFrame
        df_filled = pd.merge(all_timestamps_df, df, on='timestamp', how='left')

        # Backfill missing values (NaN)
        df_filled = df_filled.bfill()

        # replaces every -999 as a statement for missing value with a 0 to not hinder prediction
        df_filled['R1'] = df_filled['R1'].replace(-999, 0)

    except Exception as e:
        error_type = type(e).__name__
        logging.debug(f"adding missing timestamps to weather data failed. \n {error_type}: {e}")

    # Fill missing values with NaN (this is already handled by 'how=left')
    return df_filled


