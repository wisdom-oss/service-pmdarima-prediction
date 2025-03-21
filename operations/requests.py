from operations.calculations import json_reader, predictions as pred, save_load as so, weather, analysis
from dotenv import load_dotenv
import os
import warnings
import logging

# filter all future warnings we don't use.
warnings.filterwarnings('ignore', category=FutureWarning, message="'force_all_finite' was renamed to 'ensure_all_finite'")

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

def extract_single_smartmeter(meter_name, timeframe: str, resolution: str, startpoint: str):
    """
    extracts data from a single smartmeter and transforms it into json data
    :param meter_name: name of meter
    :param timeframe: relation of length
    :param resolution: resolution of data points
    :return: the created df
    """

    df = json_reader.create_df_from_smartmeter(meter_name, timeframe, resolution, startpoint)

    json_data = df.to_dict(orient="list")

    json_data["name"] = f"{meter_name}"
    json_data["timeframe"] = f"{timeframe}"
    json_data["resolution"] = f"{resolution}"

    return json_data

def load_and_use_model(meter_name: str, timeframe: str, resolution: str, startpoint: str, exogen: bool):

    model_data = so.load_model_by_name(meter_name, timeframe, resolution, startpoint, exogen)

    if isinstance(model_data, str):
        return model_data

    # create weather data to accompany predictions
    df_weather = weather.request_weather_info(model_data["labels"])

    pred_df = pred.create_forecast_data(model_data["model"], 24, df_weather)

    # add the analysis results to the request
    analysis_df = analysis.analyze_prediction(model_data["realValue"], pred_df["numValue"])


    # add bonus information back to dataframe
    json_data = pred_df.to_dict(orient="list")
    json_data["name"] = f"{meter_name}"
    json_data["timeframe"] = f"{timeframe}"
    json_data["resolution"] = f"{resolution}"
    json_data["dateObserved"] = model_data["labels"]
    json_data["realValue"] = model_data["realValue"]
    json_data["meanAbsoluteError"] = analysis_df["MAE"][0]
    json_data["meanSquaredError"] = analysis_df["MSE"][0]
    json_data["rootOfmeanSquaredError"] = analysis_df["RMSE"][0]
    json_data["r2"] = analysis_df["R2"][0]


    return json_data

def train_and_save_model(meter_name: str, timeframe: str, resolution: str, startpoint: str, exogen: bool):
    # create a dataframe based on the provided parameters
    df = json_reader.create_df_from_smartmeter(meter_name, timeframe, resolution, startpoint)

    if not so.has_duplicates(meter_name, timeframe, resolution, startpoint):

        # create date labels for the prediction models
        labels = pred.create_labels(df)

        # save the real data belonging to the prediction
        data = json_reader.create_df_from_labels(labels, meter_name, resolution)

        load_dotenv()
        labels = labels["Date"].dt.strftime(os.getenv("DATETIME_STANDARD_FORMAT")).tolist()

        # train the model based on exogenous bool
        model = pred.train_model(exogen, df)

        # save the model as well as used labels
        model_data = {
            "labels": labels,
            "model": model,
            "realValue": data
        }

        return so.save_model_by_name(model_data, meter_name, timeframe, resolution, startpoint, exogen)
    else:
        raise ValueError("model exists already!")

