from datetime import datetime
import requests
from pandas import json_normalize

def request_weather(labels: list):

    start, end = convert_timestamps(labels[0], labels[-1])

    response = requests.get(f"https://wisdom-demo.uol.de/api/dwd/00691/air_temperature/hourly?from={start}&to={end}")

    data = response.json()

    # Transform into DataFrame
    df = json_normalize(data["timeseries"])

    return df




def convert_timestamps(start: str, end: str):
    # Define the format of your timestamp
    format_string = "%d.%m.%y %H:%M"

    # Convert to a datetime object
    datetime_start = datetime.strptime(start, format_string)
    datetime_end = datetime.strptime(end, format_string)

    # Convert to Unix timestamp (seconds since epoch)
    unix_start = int(datetime_start.timestamp())
    unix_end = int(datetime_end.timestamp())

    return unix_start, unix_end

