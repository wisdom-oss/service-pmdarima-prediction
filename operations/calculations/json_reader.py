from datetime import timedelta

import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from root_file import ROOT_DIR


def create_df_from_smartmeter(meter_name, timeframe: str, resolution: str, startpoint: str) -> pd.DataFrame:
    """
    extract single smartmeter data
    :param resolution: resolution of the requested data: hourly, daily, weekly
    :param meter_name: name of smartmeter
    :param timeframe: timely frame how many rows are being extracted
    :return: json resp of meter_name and extracted values + dates
    """

    # read in whole file
    df = read_smartmeter_data(False)

    # filter every meter not being named
    df = df.drop(df[df.refDevice != meter_name].index)

    # filter out unnecessary columns
    df = df[["dateObserved", "numValue"]]

    # create start date and end date
    start, end = __gain_start_end_date(timeframe, startpoint)

    # filter df by start and end
    df = __filter_df_by_dates(df, start, end)

    # reduce data points when necessary
    df = __reduce_data_points(df, resolution)

    return df

def read_smartmeter_data(metaCheck: bool):
    """
    read in the json data
    :param metaCheck: if true, read in meta data
    :return: df containing data
    """

    abs_path = os.path.join(ROOT_DIR,
                            os.getenv("FILE_PATH_EXAMPLE_DATA"))
    if metaCheck:
        path = os.path.join(abs_path, os.getenv("EXAMPLE_META_DATA"))
    else:
        path = os.path.join(abs_path, os.getenv("EXAMPLE_DATA"))

    df = pd.read_json(path)

    return df

def create_df_from_labels(labels: pd.DataFrame, meter_name: str, resolution: str) -> list:
    """
    create real values of provided date labels
    :param labels: datetimes to filter
    :param meter_name: name of provided smartmeter
    :param resolution: timely resolution
    :return: df of numerical real measured values
    """

    df = read_smartmeter_data(False)

    # filter every meter not being named
    df = df.drop(df[df.refDevice != meter_name].index)

    df = df[["dateObserved", "numValue"]]

    df = __filter_df_by_dates(df, labels["Date"].iloc[0], labels["Date"].iloc[-1])
    df = __reduce_data_points(df, resolution)

    df = df[["numValue"]]
    df.rename(columns={"numValue": "realValue"}, inplace=True)

    # change datatype to save memory
    df["realValue"] = df["realValue"].astype("float32")

    return df["realValue"].tolist()

def __gain_start_end_date(timeframe: str, startpoint: str) -> [str, str]:
    """
    private function to map the timeframe to an end date
    :param start_point: the date to start searching
    :param timeframe: the time frame to search for (1 week, 1 month..)
    :return: the end date of the corresponding timeframe
    """

    load_dotenv()
    if startpoint:
        start_point = pd.to_datetime(startpoint)
    else:
        start_point = pd.to_datetime(os.getenv("STARTING_DATE_SMARTMETER"))

    end = 0

    match timeframe:
        case "one day":
            end = start_point + relativedelta(days=1)
        case "one week":
            end = start_point + relativedelta(weeks=1)
        case "one month":
            end = start_point + relativedelta(months=1)
        case "three months":
            end = start_point + relativedelta(months=3)
        case "six months":
            end = start_point + relativedelta(months=6)
        case "one year":
            end = start_point + relativedelta(months=12)
        case "all":
            # CAUTION WHEN HAVING MORE DATA THAN 5 years!
            end = start_point + relativedelta(months=60)

    # reduce end by 1 minute, because unix doesnt recognize lower timechanges
    # in order to invalidate the last entry,
    # so there are exactly 168 (observations + startpoint)
    end = end - timedelta(minutes=1)

    return str(start_point), str(end)

def __filter_df_by_dates(df: pd.DataFrame, start_date, end_date) -> pd.DataFrame:
    # Ensure 'dateObserved' is in datetime format
    df['dateObserved'] = pd.to_datetime(df['dateObserved'], errors='coerce')
    start_date = pd.to_datetime(start_date, errors='coerce')
    end_date = pd.to_datetime(end_date, errors='coerce')

    # Filter DataFrame
    filtered_df = df[(df['dateObserved'] >= start_date) & (df['dateObserved'] <= end_date)]

    return filtered_df

def __reduce_data_points(df, resolution: str) -> pd.DataFrame:
    # set date index
    df = df.set_index("dateObserved")

    modifier = ""

    match resolution:
        case "hourly":
            modifier = "h"
        case "daily":
            modifier = "D"
            print(f"resample data to daily values")
        case "weekly":
            modifier = "W"
            print(f"resample data to weekly values")

    avg = df.resample(modifier)["numValue"].mean()
    avg = avg.reset_index()

    return avg



