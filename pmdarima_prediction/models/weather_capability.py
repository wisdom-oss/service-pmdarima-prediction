from datetime import datetime

from pydantic import BaseModel, Field

from ..enums import SupportedCapabilities, SupportedResolutions
from .weather_column import WeatherColumn


class WeatherCapability(BaseModel):
    capability: SupportedCapabilities
    available_from: datetime = Field(alias="availableFrom")
    available_until: datetime = Field(alias="availableUntil")
    columns: list[WeatherColumn] | None
    resolution: SupportedResolutions

    class Config:
        frozen = True
