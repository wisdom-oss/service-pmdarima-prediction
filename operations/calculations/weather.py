from datetime import datetime
import pytz
import requests
from pandas import json_normalize, to_datetime
from datetime import datetime, timedelta
import pandas as pd

def request_weather_info(labels: list):

    start, end = convert_timestamps(labels[0], labels[-1])

    #capability, column_name = "air_temperature", "TT_TU"
    capability, column_name = "precipitation", "R1"

    response = requests.get(
        f"https://wisdom-demo.uol.de/api/dwd/00691/{capability}/hourly?from={start}&until={end}"
    )

    data = response.json()

    # Transform into DataFrame
    df = json_normalize(data["timeseries"])

    df = adjust_timestamp_column(df, "ts")

    df = fill_missing_timestamps(df)

    return df[[column_name]]


def convert_timestamps(start, end):
    # Check if the inputs are datetime objects or strings
    if not isinstance(start, datetime) and not isinstance(end, datetime):
        format_string = "%d.%m.%y %H:%M"  # Adjusted for your timestamp format
        # Parse the input datetime strings into naive datetime objects
        datetime_start = datetime.strptime(start, format_string)
        datetime_end = datetime.strptime(end, format_string)
    else:
        datetime_start = start
        datetime_end = end

    # Convert to Unix timestamp
    unix_start = int(datetime_start.timestamp())
    unix_end = int(datetime_end.timestamp())

    return unix_start, unix_end


def adjust_timestamp_column(df, column_name):
    # Convert the timestamp column to datetime, ensuring the format is correctly interpreted 2021-10-27T22:00:00Z

    df[column_name] = to_datetime(df[column_name], format="%Y-%m-%dT%H:%M:%SZ")

    # Adjust by 2 hours
    df[column_name] = df[column_name] + timedelta(hours=2)

    # Optionally, convert back to the original format if needed
    df[column_name] = df[column_name].dt.strftime("%d.%m.%y %H:%M")

    return df


def fill_missing_timestamps(df):
    """
    Fills missing timestamps in the DataFrame, because DWD sucks, by creating a continuous range of hourly timestamps
    and merging it with the existing data, filling missing rows with NaN.

    :param df: DataFrame with a 'timestamp' column that contains the datetime values.
    :return: A DataFrame with missing timestamps filled with NaN values.
    """

    # Ensure the 'timestamp' column is in datetime format
    df['timestamp'] = pd.to_datetime(df['ts'], format='%d.%m.%y %H:%M')

    # Create a date range from the first to the last timestamp in the DataFrame
    start_timestamp = df['timestamp'].min()
    end_timestamp = df['timestamp'].max()
    all_timestamps = pd.date_range(start=start_timestamp, end=end_timestamp, freq='H')

    # Create a DataFrame with the complete range of timestamps
    all_timestamps_df = pd.DataFrame(all_timestamps, columns=['timestamp'])

    # Merge the new date range with the original DataFrame
    df_filled = pd.merge(all_timestamps_df, df, on='timestamp', how='left')

    # Backfill missing values (NaN)
    df_filled = df_filled.fillna(method='bfill')

    # replaces every -999 as a statement for missing value with a 0 to not hinder prediction
    df_filled['R1'] = df_filled['R1'].replace(-999, 0)

    # Fill missing values with NaN (this is already handled by 'how=left')
    return df_filled


