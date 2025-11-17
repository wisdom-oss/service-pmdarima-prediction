import hashlib
from datetime import datetime
from typing import Literal, Tuple

from pendulum import now
from pydantic import UUID1, UUID4, BaseModel, Field
from pydantic_extra_types.pendulum_dt import DateTime, Duration
from pytz import utc


class SmartMeter(BaseModel):
    id: UUID4
    name: str
    description: str | None


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
    id: UUID4 = Field(alias="modelId")
    for_meter: UUID4 = Field(alias="meterId")
    start_point: DateTime | datetime | None = Field(alias="dataStartsAt")
    end_point: DateTime | datetime | None = Field(alias="dataEndsAt")
    with_weather_capability: bool = Field(alias="withWeatherCapability")
    weather_capability: SupportedCapabilities | None = Field(
        None, alias="weatherCapability"
    )
    capability_column: str | None = Field(None, alias="capabilityColumn")
    training_time: Duration | None = Field(None, alias="trainingTime")
    trained_at: DateTime | None = Field(now(), alias="trainedAt")  # type: ignore
    comment: str | None = Field(None)

    def generate_identifier(self) -> str:
        return hashlib.md5(
            bytes(
                self.model_dump_json(
                    exclude=set(["id", "training_time", "trained_at"])
                ),
                "utf-8",
            ),
            usedforsecurity=False,
        ).hexdigest()


class ConfidenceDatapoint(Datapoint):
    confidence_interval: Tuple[float, float] = Field(alias="confidenceInterval")


class Prediction(BaseModel):
    made_with_model: str = Field(alias="madeWithModel")
    mean_absolute_error: float = Field(alias="mae")
    mean_squared_error: float = Field(alias="mse")
    root_mean_squared_error: float = Field(alias="rmse")
    r2_score: float = Field(alias="r2")

    datapoints: list[ConfidenceDatapoint]


class TrainingInitiation(BaseModel):
    model_id: str = Field(alias="modelId")
    training_id: str = Field(alias="trainingId")
