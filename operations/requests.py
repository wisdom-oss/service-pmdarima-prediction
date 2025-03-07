from operations.calculations import json_reader, predictions as pred, save_load as so
from dotenv import load_dotenv
import os

def read_meter_information():
    """
    read in meta data of meter information to display the different smartmeter timeseries
    :return: list of short names of smartmeter
    """
    df = json_reader.read_smartmeter_data(True)

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

    df = json_reader.create_df_from_smartmeter(meter_name, timeframe, resolution)

    json_data = df.to_dict(orient="list")

    json_data["name"] = f"{meter_name}"
    json_data["timeframe"] = f"{timeframe}"
    json_data["resolution"] = f"{resolution}"

    return json_data

def load_and_use_model(meter_name: str, timeframe: str, resolution: str):

    model_data = so.load_model_by_name(meter_name, timeframe, resolution)

    pred_df = pred.create_forecast_data(model_data["model"], 24, None)

    # add bonus information back to dataframe
    json_data = pred_df.to_dict(orient="list")
    json_data["name"] = f"{meter_name}"
    json_data["timeframe"] = f"{timeframe}"
    json_data["resolution"] = f"{resolution}"
    json_data["dateObserved"] = model_data["labels"]

    return json_data

def train_and_save_model(meter_name: str, timeframe: str, resolution: str):
    # create a dataframe based on the provided parameters
    df = json_reader.create_df_from_smartmeter(meter_name, timeframe, resolution)

    if not so.has_duplicates(meter_name, timeframe, resolution):

        # create date labels for the prediction models
        labels = pred.create_labels(df)

        # save the real data belonging to the prediction
        #data = json_reader.create_df_from_labels(labels, meter_name, resolution)

        # train the model if identifier is unique
        model = pred.train_model(df)

        # save the model as well as used labels
        model_data = {
            "labels": labels,
            "model": model
        }

        return so.save_model_by_name(model_data, meter_name, timeframe, resolution)
    else:
        raise ValueError("model exists already!")

