from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime

from pytz import utc


class SmartMeter(BaseModel):
    id: str
    name: str


class WeatherColumn(BaseModel):
    column_name: str
    description: str
    for_data_from: datetime = Field(alias="forDataFrom")
    for_data_until: datetime = Field(alias="forDataUntil")

    def __hash__(self) -> int:
        return hash(
            (
                self.column_name,
                self.description,
                self.for_data_from.astimezone(utc).isoformat(),
                self.for_data_until.astimezone(utc).isoformat(),
            )
        )

class Datapoint(BaseModel):
    time: datetime
    value: float

SupportedResolution = Literal["hourly"]
SupportedCapabilities = Literal["air_temperature", "precipitation", "moisture"]


class WeatherCapability(BaseModel):
    capability: SupportedCapabilities
    available_from: datetime = Field(alias="availableFrom")
    available_until: datetime = Field(alias="availableUntil")
    columns: list[WeatherColumn] | None
    resolution: SupportedResolution

    class Config:
        frozen = True
