import requests
import pandas as pd
import logging
import os
from pandas import json_normalize
from dotenv import load_dotenv


def load_dwd_api() -> str | None:
    load_dotenv()
    dwd_api_raw = os.getenv("DWD_API_V1")
    weather_station = os.getenv("WEATHER_STATION")

    if not dwd_api_raw or not weather_station:
        logging.debug("DWD_API not set in .env")
        raise TypeError("DWD_API_V1 or WEATHER_STATION env variables not set")

    dwd_api = dwd_api_raw + weather_station

    return dwd_api


def get_weather_capabilities(req_cols: bool) -> dict[str, list[str]]:
    """
    return a list of all weather capabilities
    :param req_cols: True when requesting all columns as well, false else
    :return: dict of weather capabilities
    """
    response = requests.get(DWD_API)
    data = response.json()
    capabilities = {}

    min_date = pd.to_datetime("2021-05-26 00:00:00", utc=True)
    max_date = pd.to_datetime("2023-05-26 00:00:00", utc=True)

    for entry in data["capabilities"]:
        entry["availableFrom"] = pd.to_datetime(entry["availableFrom"], utc=True)
        entry["availableUntil"] = pd.to_datetime(entry["availableUntil"], utc=True)

        # rule out every datatype not having hourly data or not inside the timeframe of the data
        if entry["resolution"] != "hourly":
            logging.debug(f"{entry["dataType"]} not available, because of resolution: {entry['resolution']}")
            continue
        if entry["availableFrom"] > min_date:
            logging.debug(f"{entry["dataType"]} not available, because of MIN: {entry['availableFrom']}")
            continue
        if entry["availableUntil"] < max_date:
            logging.debug(f"{entry["dataType"]} not available, because of MAX: {entry['availableUntil']}")
            continue

        # add dict entries when requesting columns
        capabilities[entry["dataType"]] = []

    if req_cols:
        capabilities = get_columns_of_weather(capabilities)

    return capabilities


def get_columns_of_weather(capabilities: dict) -> dict[str, list[str]]:
    """
    request every column of every weather capability
    :param capabilities: dict of capabilities
    :return: dict of capabilities with column entries
    """
    MIN_DATE = pd.to_datetime("2021-05-26 00:00:00", utc=True)
    unix_start = int(MIN_DATE.timestamp())
    unix_end = int(unix_start + 60)

    for capability in capabilities:
        response = requests.get(
            DWD_API + f"/{capability}/hourly?from={unix_start}&until={unix_end}")
        data = response.json()

        if data.get("timeseries") and isinstance(data["timeseries"], list):
            for column in data["timeseries"][0]:
                logging.debug(f"{column} available")
                capabilities[capability].append(column)

    return capabilities


def get_columns_of_capability(capability: str) -> dict:
    MIN_DATE = pd.to_datetime("2021-05-26 00:00:00", utc=True)
    unix_start = int(MIN_DATE.timestamp())
    unix_end = int(unix_start + 60)

    capability_dict = {"columns": []}

    if capability != "plain":

        response = requests.get(
            DWD_API + f"/{capability}/hourly?from={unix_start}&until={unix_end}")
        data = response.json()

        if data.get("timeseries") and isinstance(data["timeseries"], list):
            for column in data["timeseries"][0]:
                if column == "ts":
                    continue
                logging.debug(f"{column} available")
                capability_dict["columns"].append(column)

    else:
        capability_dict["columns"] = ["No Weather Attribute chosen"]

    return capability_dict


def get_weather_data(capability: str, column: str, unix_start: int, unix_end: float) -> pd.DataFrame or None:
    """
    request weather data from dwd
    :param unix_start: start timestamp to search for
    :param unix_end: end timestamp to search for
    :param capability: kind of weather data to request
    :param column: column of capability to request
    """
    df = pd.DataFrame()

    if capability == "plain":
        return None

    try:
        response = requests.get(
            DWD_API + f"/{capability}/hourly?from={unix_start}&until={unix_end}"
        )
        data = response.json()

        df = json_normalize(data["timeseries"])
    except Exception as e:
        logging.debug(f"DWD request failed, because: {e}")

    # fill data spots inside weather data to fill in missing timestamps
    df = __fill_missing_timestamps(df, column)

    return df[[column, "ts"]]


def __fill_missing_timestamps(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    create missing timestamps in weather data in between start and end date
    :param df: df of weather info
    :param column_name: column to check for missing data
    :return:
    """

    # Ensure the 'timestamp' column is in datetime format
    df['ts'] = pd.to_datetime(df['ts'], format='%Y-%m-%dT%H:%M:%SZ')

    # Create a date range from the first to the last timestamp in the DataFrame
    all_timestamps = pd.date_range(start=df['ts'].min(), end=df['ts'].max(), freq='h')
    all_timestamps_df = pd.DataFrame(all_timestamps, columns=['ts'])

    # Merge the new date range with the original DataFrame
    df_filled = pd.merge(all_timestamps_df, df, on='ts', how='left')

    # backfill missing values (NaN)
    df_filled = df_filled.bfill()

    # replaces every -999 as a statement for missing value with a 0 to not hinder prediction
    df_filled[column_name] = df_filled[column_name].replace(-999, 0)

    return df_filled


DWD_API: str = load_dwd_api()
