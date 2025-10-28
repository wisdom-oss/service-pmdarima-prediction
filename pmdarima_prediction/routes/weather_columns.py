from .. import app

from pydantic import BaseModel
from ..classes import SupportedCapabilities, SupportedResolution, WeatherCapability
from ..weather import API as weather_api
from datetime import datetime
from flask_pydantic import validate


class _QueryParams(BaseModel):
    capability: list[SupportedCapabilities] | None = None
    resolution: SupportedResolution = "hourly"
    start: datetime = datetime(2021, 5, 26, 0, 0, 0)
    end: datetime = datetime(2023, 5, 26)


@app.get("/weather-columns")
@validate(response_many=True)
async def get_weather_columns(query: _QueryParams) -> list[WeatherCapability]:
    return await weather_api.get_available_capability_columns(
        start=query.start,
        end=query.end,
        for_capabilities=query.capability,
        resolution=query.resolution,
    )
