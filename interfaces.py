import datetime
from typing import TypedDict


class SmartmeterData(TypedDict):
    date: list[str]
    name: str
    resolution: str
    timeframe: str
    value: list[float]

class ForecastData(TypedDict):
    aic: float
    date: list[str]
    fit_time: float
    lower_conf_values: list[float]
    meanAbsoluteError: float
    meanSquaredError: float
    name: str
    realValue: list[float]
    resolution: str
    rootMeanSquaredError: float
    r2: float
    timeframe: str
    upper_conf_values: list[float]
    value: list[float]

class FetchOneQueryDict(TypedDict):
    date: list[datetime.datetime]
    value: list[float]

class SelectDateValueData(TypedDict):
    date: list[datetime.datetime]
    value: list[float]