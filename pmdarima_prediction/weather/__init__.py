import asyncio
import urllib
import urllib.parse
from datetime import datetime
from typing import Annotated, Any, get_args

import aiohttp
import dateutil
import httpx
from pydantic import BaseModel, HttpUrl, ValidationError
from pydantic.types import StringConstraints
from pytz import utc

from pmdarima_prediction.classes import SupportedResolution

from .. import config
from ..enums import SupportedCapabilities, SupportedResolutions
from ..exceptions.service_error import ServiceException
from ..models.weather_capability import WeatherCapability
from ..models.weather_column import WeatherColumn


class _api(BaseModel):
    """
    The main entry point for interacting with the WISdoM DWD Proxy
    """

    base_url: HttpUrl
    station_id: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=5, max_length=5, pattern=r"\d{5}"
        ),
    ]

    async def get_available_capabilities(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        resolution: SupportedResolutions | None = None,
    ) -> list[WeatherCapability]:
        """
        Get the available capabilites of the configured station

        :param start: The time after which a capability should be considered
            available
        :type start: datetime | None
        :param end: The time before which a capability should be considered
            available
        :type end: datetime | None
        :return: The list of unique WeatherCapabilities
        :rtype: list[WeatherCapability]
        """

        url = urllib.parse.urljoin(
            base=self.base_url.encoded_string(), url=f"v1/{self.station_id}"
        )

        response = httpx.get(url)

        station_details: dict[str, Any] = response.json()
        station_capabilities = (
            station_details["capabilities"]
            if "capabilities" in station_details.keys()
            else None
        )

        if station_capabilities is None:
            raise ServiceException(
                type="",
                status=500,
                title="Configured Station Without Capabilities",
                details="The service has been configured to use a station without any weather capabilities",
            )

        capabilities: set[WeatherCapability] = set()
        for station_capability in station_capabilities:
            print(station_capability)
            available_from = dateutil.parser.isoparse(
                station_capability["availableFrom"]
            )
            available_until = dateutil.parser.isoparse(
                station_capability["availableUntil"]
            )

            if start is not None:
                if available_until < start:
                    continue

            if end is not None:
                if available_from > end:
                    continue

            if (
                resolution is not None
                and station_capability["resolution"] != resolution
            ):
                continue

            # Check if the resolution adheres to the literals SupportedResolution
            # and if the data type is one of the supported capabilities
            try:
                assert station_capability["resolution"] in get_args(
                    SupportedResolutions._member_names_
                )
                assert station_capability["dataType"] in get_args(
                    SupportedCapabilities._member_names_
                )
            except AssertionError:
                continue

            try:
                capability = WeatherCapability(
                    capability=station_capability["dataType"],
                    columns=None,
                    availableFrom=available_from,
                    availableUntil=available_until,
                    resolution=station_capability["resolution"],
                )

                capabilities.add(capability)
            except ValidationError:
                pass

        return [capability for capability in capabilities]

    async def get_available_capability_columns(
        self,
        resolution: SupportedResolutions | None = SupportedResolutions.hourly,
        start: datetime | None = None,
        end: datetime | None = None,
        for_capabilities: list[SupportedCapabilities]
        | list[WeatherCapability]
        | None = None,
    ) -> list[WeatherCapability]:
        """
        Docstring for get_available_capabilities

        :param start: Description
        :type start: datetime
        :param end: Date Range after which a columm
        :type end: datetime
        :param for_capabilities: The capability identifiers which the columns
          should be requested for. If no list is supplied then all possible
          capabilities will be pulled and returned
        :type for_capabilities: list[str] | None
        :return: A list of WeatherCapabilities outlining which capability has
          which columns
        :rtype: list[WeatherCapability]
        """

        params: dict[str, str] = dict()
        if start is not None:
            start = start.astimezone(utc)
        else:
            start = datetime(year=0, month=0, day=0).astimezone(utc)
        params["start"] = start.isoformat()

        if end is not None:
            end = end.astimezone(utc)
        else:
            end = datetime.now().astimezone(utc)
        params["end"] = end.isoformat()

        if for_capabilities is None:
            for_capabilities = await self.get_available_capabilities()

        urls: set[tuple[str, str]] = set()

        for requested_capability in for_capabilities:
            if isinstance(requested_capability, WeatherCapability):
                urls.add(
                    (
                        requested_capability.capability,
                        urllib.parse.urljoin(
                            base=self.base_url.encoded_string(),
                            url=(
                                f"v2/timeseries/climateObservations/{requested_capability.capability}/{requested_capability.resolution}/{self.station_id}?{urllib.parse.urlencode(params)}"
                            ),
                        ),
                    )
                )
            if requested_capability in get_args(SupportedCapabilities):
                urls.add(
                    (
                        str(requested_capability),
                        urllib.parse.urljoin(
                            base=self.base_url.encoded_string(),
                            url=(
                                f"v2/timeseries/climateObservations/{requested_capability}/{resolution}/{self.station_id}?{urllib.parse.urlencode(params)}"
                            ),
                        ),
                    )
                )

        capabilities: list[WeatherCapability] = []
        results: list[tuple[str, dict[str, Any]]] = []

        async with aiohttp.ClientSession() as session:
            tasks = [
                self.__do_request_for_json(session, url[1], url[0]) for url in urls
            ]
            results = await asyncio.gather(*tasks)

        for result in results:
            data_type, data = result
            if "metadata" not in data.keys():
                continue

            columns: set[WeatherColumn] = set()

            for field in data["metadata"]:
                field_from = dateutil.parser.isoparse(field["forDataFrom"])
                field_until = dateutil.parser.isoparse(field["forDataUntil"])

                if start > field_until or end < field_from:
                    continue

                column = WeatherColumn(
                    name=field["name"],
                    description=field["description"],
                    for_data_from=field_from,
                    for_data_until=field_until,
                )
                columns.add(column)

            capability = WeatherCapability(
                capability=SupportedCapabilities(data_type),
                columns=list(columns),
                availableFrom=start,
                availableUntil=end,
                resolution=SupportedResolutions.hourly,
            )
            capabilities.append(capability)

        return capabilities

    async def get_data(
        self,
        capability: SupportedCapabilities,
        granularity: SupportedResolution = "hourly",
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> Any:
        params: dict[str, str] = dict()
        if start is not None:
            start = start.astimezone(utc)
        else:
            start = datetime(year=0, month=0, day=0).astimezone(utc)
        params["start"] = start.isoformat()

        if end is not None:
            end = end.astimezone(utc)
        else:
            end = datetime.now().astimezone(utc)
        params["end"] = end.isoformat()

        url = urllib.parse.urljoin(
            base=self.base_url.encoded_string(),
            url=(
                f"v2/timeseries/climateObservations/{capability}/{granularity}/{self.station_id}?{urllib.parse.urlencode(params)}"
            ),
        )

        data: dict[str, Any] = dict()

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ServiceException(
                        "",
                        500,
                        "Weather API Failure",
                        "Unable to connect tot the Weather API",
                    )

                data = await response.json()

        print(data)

    async def __do_request_for_json(
        self,
        session: aiohttp.ClientSession,
        url: str,
        key: str,
    ) -> tuple[str, dict[str, Any]]:
        async with session.get(url) as response:
            if response.status != 200:
                return key, dict()
            data = await response.json()
            return key, data


API: _api = _api(base_url=config.dwd_proxy_base_api, station_id=config.dwd_station_id)
