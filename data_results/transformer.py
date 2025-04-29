import pandas as pd

from weather import dwd_weather
from dateutil.relativedelta import relativedelta
import datetime
from database import data_selector as ds
from forecasting import model_training, data_forecast, model_metrics
from data_results import save_load_models

def get_meternames() -> dict or None:
    """
    get all different smartmeter names
    :return: dict with list of names
    """
    return ds.select_names()

def get_weather_capabilities(columns: bool) -> dict:
    """
    request weather capabilities
    :param columns: if true -> also columns, false else
    :return: dict of weather capabilities
    """
    return dwd_weather.get_weather_capabilities(columns)

def get_columns_of_capability(capability: str) -> dict:
    """
    request weather capabilities
    :param columns: if true -> also columns, false else
    :return: dict of weather capabilities
    """
    return dwd_weather.get_columns_of_capability(capability)

def get_smartmeter_data(meter_name: str, timeframe: str, resolution: str, start_date: str) -> dict or None:
    """
    create a dict from parameters containing real values and datetimes
    :param meter_name: name of selected smartmeter
    :param timeframe: timeframe of the request
    :param resolution: resolution of requested data
    :param start_date: first date of requested data
    :return: dict of data with parameters added
    """

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")

    end_date = create_end_date(timeframe, start_date)
    data = ds.select_date_value(meter_name, start_date, end_date)

    data["name"] = f"{meter_name}"
    data["timeframe"] = f"{timeframe}"
    data["resolution"] = f"{resolution}"

    return data

def create_end_date(timeframe: str, start_point: datetime) -> datetime:
    """
    private function to map the timeframe to an end date
    :param start_point: the date to start searching
    :param timeframe: the time frame to search for (1 week, 1 month..)
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

    # reduce end by 1 minute, because unix doesn't recognize lower timechanges
    # in order to invalidate the last entry,
    # so there are exactly 168 (observations + startpoint)
    end = end - datetime.timedelta(hours=1)

    return end

def train_model(meter_name: str, timeframe: str, resolution: str, start_date_string: str, weather_capability: str, column_name: str) -> dict or None:
    """
    train a autoarima model based on parameters
    :param meter_name: name of smartmeter to train
    :param timeframe: amount of weeks
    :param resolution: data resolution
    :param start_date_string: first date of requested data
    :param weather_capability: capability of dwd weather
    :param column_name: column name of dwd data
    :return: None
    """

    b_utc = pd.to_datetime(start_date_string, utc=True)

    a_start = datetime.datetime.strptime(start_date_string, "%Y-%m-%d %H:%M:%S")
    a_utc = a_start.replace(tzinfo=datetime.timezone.utc)


    start_date = datetime.datetime.strptime(start_date_string, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
    end_date = create_end_date(timeframe, start_date).replace(tzinfo=datetime.timezone.utc)
    start = int(start_date.timestamp())
    end = int(end_date.timestamp())

    data = ds.select_date_value(meter_name, start_date, end_date)
    df = pd.DataFrame.from_dict(data)

    weather_df = dwd_weather.get_weather_data(weather_capability, column_name, start, end)

    model, train_time = model_training.train_model(df[["value"]], weather_df[[column_name]])

    model_dict = {
        "model": model,
        "training_time": train_time,
        "start_date": start_date,
        "end_date": end_date,
    }

    save_load_models.save_model_by_name(model_dict, meter_name, timeframe, resolution, start_date_string, weather_capability, column_name)

def forecast(meter_name: str, timeframe: str, resolution: str, start_date: str, weather_capability: str, column_name: str) -> dict or None:
    """
    predict data based on parameters
    :param meter_name: name of smartmeter
    :param timeframe: amount of weeks
    :param resolution: data resolution
    :param start_date: first date
    :param weather_capability: from dwd
    :param column_name: from dwd
    :return: json representation of metrics and parameters
    """

    # load model by parameters
    model_dict = save_load_models.load_model_by_name(meter_name, timeframe, resolution, start_date, weather_capability, column_name)

    # create 24 forecast label dates
    forecast_labels = data_forecast.create_forecast_labels(model_dict["end_date"],24, resolution)

    # use labels to get weather info
    weather_df = dwd_weather.get_weather_data(weather_capability, column_name, int(forecast_labels[0].timestamp()), int(forecast_labels[-1].timestamp()))

    # use model and weather info to get predicted data
    forecast_df = data_forecast.create_forecast_data(model_dict["model"], 24, weather_df[[column_name]])

    # select real values to compare with predicted data
    real_values = ds.select_date_value(meter_name, forecast_labels[0], forecast_labels[-1])["value"]

    # evaluate model prediction
    metrics_df = model_metrics.calculate_metrics(real_values, forecast_df["value"])

    # change labels to string repr
    forecast_labels = [dt_index.strftime("%Y-%m-%dT%H:%M:%S") for dt_index in forecast_labels]

    # build dict data object
    data = forecast_df.to_dict(orient="list")
    data["name"] = f"{meter_name}"
    data["timeframe"] = f"{timeframe}"
    data["resolution"] = f"{resolution}"
    data["dateObserved"] = forecast_labels
    data["realValue"] = real_values
    data["aic"] = model_dict["model"].aic()
    data["fit_time"] = model_dict["training_time"]
    data["meanAbsoluteError"] = metrics_df["MAE"][0]
    data["meanSquaredError"] = metrics_df["MSE"][0]
    data["rootOfmeanSquaredError"] = metrics_df["RMSE"][0]
    data["r2"] = metrics_df["R2"][0]

    return data



