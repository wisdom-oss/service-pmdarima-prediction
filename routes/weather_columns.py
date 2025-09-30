from __main__ import app

from pydantic import BaseModel
from classes import SupportedCapabilities, SupportedResolution, WeatherCapability
from weather import API as weather_api
from datetime import datetime
from flask_pydantic import validate


class queryParams(BaseModel):
    capability: list[SupportedCapabilities] | None = None
    granularity: SupportedResolution = "hourly"
    start: datetime = datetime(2021, 5, 26, 0, 0, 0)
    end: datetime = datetime(2023, 5, 26)


@app.get("/weather-columns")
@validate(response_many=True)
async def get_weather_columns(query: queryParams) -> list[WeatherCapability]:
    return await weather_api.get_available_capability_columns(
        start=query.start,
        end=query.end,
        for_capabilities=query.capability,
        granularity=query.granularity,
    )
