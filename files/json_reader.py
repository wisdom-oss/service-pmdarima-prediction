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

    data = {"data": df["id"].to_list()}
    return jsonify(data)

def extract_single_smartmeter(meter_name, timeframe: str):
    """
    extract single smartmeter data
    :param meter_name: name of smartmeter
    :param timeframe: timely frame how many rows are being extracted
    :return: json resp of meter_name and extracted values + dates
    """

    df = read_smartmeter_data(False)

    # filter every meter not being named
    df = df.drop(df[df.refDevice != meter_name].index)

    df = df[["dateObserved", "numValue"]]

    load_dotenv()

    # extract start_point and convert to timestamp
    start_point = pd.to_datetime(os.getenv("STARTING_DATE_SMARTMETER"))
    df["dateObserved"] = pd.to_datetime(df["dateObserved"])

    # find the end date to request based on the timeframe
    end = __calculate_end_date(start_point, timeframe)

    # filter df based on date and convert to right format as strings
    filtered_df = df[(df["dateObserved"] >= start_point) & (df["dateObserved"] < end)]

    filtered_df = __reduce_data_points(timeframe, filtered_df)

    # ignore warning
    pd.options.mode.chained_assignment = None  # default='warn'
    filtered_df["dateObserved"] = filtered_df["dateObserved"].dt.strftime("%d.%m.%y %H:%M:%S")

    json_data = filtered_df.to_dict(orient="list")

    json_data["name"] = f"{meter_name} {timeframe}"

    return jsonify(json_data)

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

    return end

def __reduce_data_points(timeframe, df):

    if timeframe == "one day" or timeframe == "one week" or timeframe == "one month":
        return df

    # Set the 'dateObserved' column as the index
    df.set_index('dateObserved', inplace=True)

    # Resample the data by day and calculate the average of 'numValue'
    daily_avg = df.resample('D')['numValue'].mean().reset_index()

    return daily_avg
