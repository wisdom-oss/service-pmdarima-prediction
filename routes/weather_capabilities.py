from __main__ import app
from classes import SupportedResolution, WeatherCapability
from weather import API as weather_api
from datetime import datetime
from flask_pydantic import validate
from pydantic import BaseModel


class queryParameter(BaseModel):
    start: datetime | None = None
    end: datetime | None = None
    resolution: SupportedResolution | None = None


@app.get("/weather-capabilities")
@validate(response_many=True)
async def get_weather_capabilities(query: queryParameter) -> list[WeatherCapability]:
    return await weather_api.get_available_capabilities(
        start=query.start,
        end=query.end,
        resolution=query.resolution,
    )
