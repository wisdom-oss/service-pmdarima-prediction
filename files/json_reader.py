import pandas as pd
import os
from flask import jsonify
from files import transformer as t


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


def extract_single_smartmeter(meter_name:str, timeframe:str, startingTime: str):
    """
    read in smartmeter data based on which smartmeter to extract and how many rows to utilize
    :param meter_name: name of the refDevice
    :optional param nrows: number of rows to process
    :return: the shortened dataframe
    """

    df = read_smartmeter_data(False)

    json_data = t.transform_single_meter_request(df, meter_name, timeframe, startingTime)

    return jsonify(json_data)
