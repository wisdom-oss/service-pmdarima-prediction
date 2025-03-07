import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from root_file import ROOT_DIR


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

def create_df_from_smartmeter(meter_name, timeframe: str, resolution: str):
    """
    extract single smartmeter data
    :param resolution: resolution of the requested data: hourly, daily, weekly
    :param meter_name: name of smartmeter
    :param timeframe: timely frame how many rows are being extracted
    :return: json resp of meter_name and extracted values + dates
    """

    df = read_smartmeter_data(False)

    # filter every meter not being named
    df = df.drop(df[df.refDevice != meter_name].index)

    df = df[["dateObserved", "numValue"]]

    # extract start point of data and calculate end point
    load_dotenv()
    start = pd.to_datetime(os.getenv("STARTING_DATE_SMARTMETER"))
    end = __calculate_end_date(start, timeframe)

    df = __filter_df_by_endpoint(df, start, end)
    df = __reduce_data_points(df, resolution)

    return df

def create_df_from_labels(labels: pd.DataFrame, meter_name: str, resolution: str):
    """
    extract single smartmeter data
    :param resolution: resolution of the requested data: hourly, daily, weekly
    :param meter_name: name of smartmeter
    :param timeframe: timely frame how many rows are being extracted
    :return: json resp of meter_name and extracted values + dates
    """

    df = read_smartmeter_data(False)

    # filter every meter not being named
    df = df.drop(df[df.refDevice != meter_name].index)

    df = df[["dateObserved", "numValue"]]

    start = labels[0]
    end = labels[-1]

    df = __filter_df_by_endpoint(df, start, end)
    df = __reduce_data_points(df, resolution)

    return df

def __calculate_end_date(start_point, timeframe):
    """
    private function to map the timeframe to an end date
    :param start_point: the date to start searching
    :param timeframe: the time frame to search for (1 week, 1 month..)
    :return: the end date of the corresponding timeframe
    """

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
            # BUGGED -> OutOfBounds
            end = start_point + relativedelta(years=1)
        case "all":
            pass

    return end

def __filter_df_by_endpoint(df, start, end: str):
    # extract start_point and convert to timestamp
    df.dateObserved = pd.to_datetime(df.dateObserved)
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    if end:
        if end != start:
            filtered_df = df[(df["dateObserved"] >= start) & (df["dateObserved"] < end)]
        else:
            filtered_df = df
    else:
        filtered_df = df

    return filtered_df

def __reduce_data_points(df, resolution: str):
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

