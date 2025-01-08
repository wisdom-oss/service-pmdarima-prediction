import pandas as pd
import os
from flask import jsonify


def read_smartmeter_data():
    abs_path = (os.path.abspath("").replace("\\", "/") + "/smartmeterdata/example_pm_measurements.json")
    df = pd.read_json(abs_path)

    return df

def get_meter_information():
    df = read_smartmeter_data()
    df = df['refDevice']

    ls = []
    for entry in df:
        if entry in ls:
            pass
        else:
            ls.append(entry)

    data = {"data": ls}
    return jsonify(data)


def extract_single_smartmeter(meter_short_name, *nrows: int):
    """
    read in smartmeter data based on which smartmeter to extract and how many rows to utilize
    :param meter_short_name: single/family/atypical/retired
    :optional param nrows: number of rows to process
    :return: the shortened dataframe
    """

    df = read_smartmeter_data()

    # filter every meter not being named
    df = df.drop(df[df.refDevice != f"urn:ngsi-ld:Device:{meter_short_name}-household"].index)

    meter_name = df.refDevice.iloc[0]

    df = df[["dateObserved", "numValue"]]

    if nrows:
        # index 0, nrows is a tuple -> optional argument
        df = df.iloc[:nrows[0]]

    json_data = df.to_dict(orient="list")

    json_data["name"] = meter_name

    return jsonify(json_data)
