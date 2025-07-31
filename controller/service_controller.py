from typing import cast

import pandas as pd
import datetime
import os

from dotenv import load_dotenv

from interfaces import SelectDateValueData
from weather import dwd_weather
from dateutil.relativedelta import relativedelta
from database import data_selector as ds
from forecasting import model_training, data_forecast, model_metrics
from controller import model_handling
import interfaces


def get_meter_names() -> dict[str, str] | None:
    """
    get all different smartmeter names
    
    :return: dict with list of names
    """

    query_dict = ds.select_names()

    dict = {}

    for item in query_dict["names"]:
        dict[item] = f"{item.split("-")[0]} {item.split("-")[1]}"

    return dict


def get_weather_capabilities(columns: bool) -> dict[str, list[str]]:
    """
    request weather capabilities
    
    :param columns: if true -> also columns, false else
    :return: dict of weather capabilities
    """
    return dwd_weather.get_weather_capabilities(columns)


def get_columns_of_capability(capability: str) -> dict[str, list[str]]:
    """
    request columns of capability
    
    :param capability: str repr of capability
    :return: result_dict of columns
    """

    query_dict = dwd_weather.get_columns_of_capability(capability)

    result_dict = {}

    for item in query_dict["columns"]:
        result_dict[item] = item

    return result_dict


def get_smartmeter_data(meter_name: str, timeframe: str, resolution: str, start_date: str) -> interfaces.SmartmeterData | None:
    """
    create a dict from parameters containing real values and date times
    
    :param meter_name: name of selected smartmeter
    :param timeframe: timeframe of the request
    :param resolution: resolution of requested data
    :param start_date: first date of requested data
    :return: dict of data with parameters added
    """

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")

    end_date = create_end_date(timeframe, start_date)
    data = ds.select_date_value(meter_name, start_date, end_date)
    data = dict(__resample_data(data, resolution))

    load_dotenv()
    format = os.getenv("DATETIME_STANDARD_FORMAT")
    data["date"] = [x.strftime(format) for x in data["date"]]

    data["name"] = f"{meter_name}"
    data["timeframe"] = f"{timeframe}"
    data["resolution"] = f"{resolution}"

    data = cast(interfaces.SmartmeterData, data)

    return data


def create_end_date(timeframe: str, start_point: datetime.datetime) -> datetime.datetime:
    """
    private function to map the timeframe to an end date
    :param start_point: the date to start searching
    :param timeframe: the time frame to search for (1 week, 1 month.)
    :return: the end date of the corresponding timeframe
    """

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
            end = start_point + relativedelta(months=24)

    # reduce end by 1 minute, because unix doesn't recognize lower time changes
    # in order to invalidate the last entry,
    # so there are exactly 168 (observations + startpoint)
    end = end - datetime.timedelta(hours=1)

    return end


def train_model(meter_name: str, timeframe: str, resolution: str, start_date_string: str, weather_capability: str,
                column_name: str):
    """
    train auto arima model based on parameters
    
    :param meter_name: name of smartmeter to train
    :param timeframe: amount of weeks
    :param resolution: data resolution
    :param start_date_string: first date of requested data
    :param weather_capability: capability of dwd weather
    :param column_name: column name of dwd data
    :return: None
    """

    start_date = datetime.datetime.strptime(start_date_string, "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=datetime.timezone.utc)
    end_date = create_end_date(timeframe, start_date).replace(tzinfo=datetime.timezone.utc)
    start = int(start_date.timestamp())
    end = int(end_date.timestamp())

    data = ds.select_date_value(meter_name, start_date, end_date)
    df = pd.DataFrame.from_dict(cast(dict, data))

    if weather_capability == "plain":
        model, train_time = model_training.train_model(df[["value"]], None)
    else:
        weather_df = dwd_weather.get_weather_data(weather_capability, column_name, start, end)
        model, train_time = model_training.train_model(df[["value"]], weather_df[[column_name]])

    model_dict: interfaces.ModelInfoDict = {
        "model": model,
        "training_time": train_time,
        "start_date": start_date,
        "end_date": end_date,
    }

    model_handling.save_model_by_name(model_dict, meter_name, timeframe, resolution, start_date_string,
                                      weather_capability, column_name)


def forecast(meter_name: str, timeframe: str, resolution: str, start_date: str, weather_capability: str,
             column_name: str) -> interfaces.ForecastData | None:
    """
    predict data based on parameters
    
    :param meter_name: name of smartmeter
    :param timeframe: amount of weeks
    :param resolution: data resolution
    :param start_date: first date
    :param weather_capability:
    :param column_name:
    :return: json representation of metrics and parameters
    """

    # load model by parameters
    model_dict = model_handling.load_model_by_name(meter_name, timeframe, resolution, start_date, weather_capability,
                                                   column_name)

    # create 24 forecast label dates
    forecast_labels = data_forecast.create_forecast_labels(model_dict["end_date"], 24, resolution)

    # use model and weather info to get predicted data
    if weather_capability == "plain":
        forecast_df = data_forecast.create_forecast_data(model_dict["model"], 24, None)
    else:
        # use labels to get weather info
        weather_df = dwd_weather.get_weather_data(weather_capability, column_name, int(forecast_labels[0].timestamp()),
                                                  int(forecast_labels[-1].timestamp()))

        forecast_df = data_forecast.create_forecast_data(model_dict["model"], 24, weather_df[[column_name]])

    # select real values to compare with predicted data
    real_values = ds.select_date_value(meter_name, forecast_labels[0], forecast_labels[-1])["value"]

    # evaluate model prediction
    metrics_df = model_metrics.calculate_metrics(real_values, forecast_df["value"])

    # change labels to string repr
    load_dotenv()
    format = os.getenv("DATETIME_STANDARD_FORMAT")
    forecast_labels = [dt_index.strftime(format) for dt_index in forecast_labels]

    # build dict data object
    data = forecast_df.to_dict(orient="list")
    data["name"] = f"{meter_name}"
    data["timeframe"] = f"{timeframe}"
    data["resolution"] = f"{resolution}"
    data["date"] = forecast_labels
    data["realValue"] = real_values
    data["aic"] = model_dict["model"].aic()
    data["fit_time"] = model_dict["training_time"]
    data["meanAbsoluteError"] = metrics_df["MAE"][0]
    data["meanSquaredError"] = metrics_df["MSE"][0]
    data["rootOfmeanSquaredError"] = metrics_df["RMSE"][0]
    data["r2"] = metrics_df["R2"][0]

    data = cast(interfaces.ForecastData, data)

    return data


def __resample_data(data: interfaces.SelectDateValueData, resolution: str) -> interfaces.SelectDateValueData:
    """
    resamples the requested data from db using pandas

    :param data: data requested
    :param resolution: new resolution to transform
    :return: dict of same parameters as input

    add further in trainmodel and forecast
    """
    df = pd.DataFrame.from_dict(dict(data))
    df.set_index("date", inplace=True)

    if resolution == "hourly":
        resolution = "h"
    elif resolution == "daily":
        resolution = "D"
    elif resolution == "weekly":
        resolution = "7D" # solid 7day chunks instead of weekly bins ("W")
    else:
        raise ValueError("Unsupported resolution")

    agg_df = df.resample(resolution).mean()
    agg_df = agg_df.reset_index()

    data = agg_df.to_dict(orient="list")

    return data

