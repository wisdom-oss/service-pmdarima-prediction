from datetime import datetime

from flask_pydantic import validate  # type: ignore
from pydantic import BaseModel

from .. import app
from ..enums import SupportedResolutions
from ..models import WeatherCapability
from ..weather import API as weather_api


class _QueryParams(BaseModel):
    start: datetime | None = None
    end: datetime | None = None
    resolution: SupportedResolutions | None = None


@app.get("/weather-capabilities")
@validate(response_many=True)
async def get_weather_capabilities(query: _QueryParams) -> list[WeatherCapability]:
    return await weather_api.get_available_capabilities(
        start=query.start,
        end=query.end,
        resolution=query.resolution,
    )
