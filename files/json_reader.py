import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from flask import jsonify
from dotenv import load_dotenv


def read_smartmeter_data(metaCheck: bool):
    """
    read in the json data
    :param metaCheck: if true, read in meta data
    :return: df containing data
    """

    abs_path = (os.path.abspath("").replace("\\", "/") + "/files/smartmeterdata")

    if metaCheck:
        path = abs_path + "/example_pm_meta.json"
    else:
        path = abs_path + "/example_pm_measurements.json"


    df = pd.read_json(path)
    return df

def read_meter_information():
    df = read_smartmeter_data(True)

    load_dotenv()
    prefix = os.getenv("DEVICE_PREFIX")

    short_handles = {}

    for item in df["id"].to_list():
        if prefix in item:
            short = item.replace(prefix, "")
            short_handles[item] = short

    return short_handles

def extract_single_smartmeter(meter_name, timeframe: str, resolution: str):
    """
    extracts data from a single smartmeter and transforms it into json data
    :param meter_name: name of meter
    :param timeframe: relation of length
    :param resolution: resolution of data points
    :return: the created df
    """

    df = create_df_from_smartmeter(meter_name, timeframe, resolution)

    json_data = df.to_dict(orient="list")

    json_data["name"] = f"{meter_name}"
    json_data["timeframe"] = f"{timeframe}"
    json_data["resolution"] = f"{resolution}"

    return json_data

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

    # filter df by start and end
    df = __filter_df_by_endpoint(df, start, end)

    df = __reduce_data_points(df, resolution)

    df = __change_label_data(df, resolution)

    return df

def __calculate_end_date(start_point, timeframe):
    """
    private function to map the timeframe to an end date
    :param start_point: the date to start searching
    :param timeframe: the time frame to search for (1 week, 1 month..)
    :return: the end date of the corresponding timeframe
    """

    end = start_point

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
    df["dateObserved"] = pd.to_datetime(df["dateObserved"])

    if end != start:
        filtered_df = df[(df["dateObserved"] >= start) & (df["dateObserved"] < end)]
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
            print("resample data to daily values")
        case "weekly":
            modifier = "W"
            print("resample data to weekly values")

    avg = df.resample(modifier)["numValue"].mean()
    avg = avg.reset_index()

    return avg

def __change_label_data(df, resolution):

    match resolution:
        case "hourly":
            # use day and time format
            df["dateObserved"] = df["dateObserved"].dt.strftime("%d.%m.%y %H:%M")
        case "daily":
            # only use day format
            df["dateObserved"] = df["dateObserved"].dt.strftime("%d.%m.%y")
        case "weekly":
            # use calender week format
            df["dateObserved"] = df["dateObserved"].dt.strftime("%V-%y")

    return df
