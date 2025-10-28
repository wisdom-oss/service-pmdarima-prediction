import hashlib
from typing import Literal, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from pendulum import now

from pydantic_extra_types.pendulum_dt import DateTime, Duration
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
    value: int | float


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


class ModelMetaData(BaseModel):
    for_meter: str = Field(alias="meter")
    start_point: DateTime | datetime = Field(alias="startingPoint")
    time_span: Duration | None = Field(alias="timeSpan")
    with_weather_capability: bool = Field(alias="withWheaterCapability")
    weather_capability: SupportedCapabilities | None = Field(
        None, alias="weatherCapability"
    )
    column_name: str | None = Field(None, alias="columnName")
    training_time: Duration | None = Field(None, alias="trainingTime")
    trained_at: DateTime | None = Field(now(), alias="trainedAt") # type: ignore

    def generate_identifier(self) -> str:
        return hashlib.md5(
            bytes(
                self.model_dump_json(exclude=set(["training_time", "trained_at"])),
                "utf-8",
            ),
            usedforsecurity=False,
        ).hexdigest()


class ConfidenceDatapoint(Datapoint):
    confidence_interval: Tuple[float, float]


class Prediction(BaseModel):
    made_with_model: str = Field(alias="madeWithModel")
    mean_absolute_error: float = Field(alias="mae")
    mean_squared_error: float = Field(alias="mse")
    root_mean_squared_error: float = Field(alias="rmse")
    r2_score: float = Field(alias="r2")

    datapoints: list[ConfidenceDatapoint]
