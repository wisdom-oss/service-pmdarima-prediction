from datetime import datetime
from typing import Any, TypedDict
from pmdarima import ARIMA
from werkzeug.exceptions import HTTPException
from werkzeug.sansio.response import Response
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.wrappers.request import Request
from werkzeug.wrappers.response import Response as WSGIResponse
import typing as t
from json import dumps
import platform
from time import gmtime, strftime


class SmartmeterData(TypedDict):
    date: list[str]
    name: str
    resolution: str
    timeframe: str
    value: list[float]


class ForecastData(TypedDict):
    aic: float
    date: list[str]
    fit_time: float
    lower_conf_values: list[float]
    meanAbsoluteError: float
    meanSquaredError: float
    name: str
    realValue: list[float]
    resolution: str
    rootMeanSquaredError: float
    r2: float
    timeframe: str
    upper_conf_values: list[float]
    value: list[float]


class FetchOneQueryDict(TypedDict):
    date: list[datetime]
    value: list[float]


class SelectDateValueData(TypedDict):
    date: list[datetime]
    value: list[float]


class ModelInfoDict(TypedDict):
    end_date: datetime
    model: ARIMA
    start_date: datetime
    training_time: float


class ServiceError(HTTPException):
    """
    # ServiceError

    Extends :py:class:`werkzeug.exceptions.HTTPException` to support RFC 9457.
    """

    type: str
    status: int
    title: str
    detail: str
    instance: str
    errors: list[Exception] | None
    host: str

    def __init__(
        self, type: str, status: int, title: str, detail: str, errors: list[Exception] | None = None
    ) -> None:
        self.type = type
        self.status = status
        self.title = title
        self.detail = detail
        self.errors = errors

    def get_headers(
        self, environ: dict[str, Any] | None = None, scope: dict[str, Any] | None = None
    ) -> list[tuple[str, str]]:
        return [("Content-Type", "application/problem+json; charset=utf-8")]

    def get_body(
        self,
        environ: Any | None = None,
        scope: dict[str, t.Any] | None = None,
    ) -> str:
        if self.type == "":
            self.type = "https://werkzeug.palletsprojects.com/en/stable/exceptions/#werkzeug.exceptions.HTTPException"

        data: dict[str, Any] = {
            "type": self.type,
            "status": self.status,
            "title": (
                self.title.strip()
                if self.title.strip() != ""
                else HTTP_STATUS_CODES.get(self.status, "Unknown Error")
            ),
            "detail": self.detail,
            "instance": f"tag:{platform.node()},{strftime("%Y-%m-%d", gmtime())}:{self.convert_camel_case(self.title)}:{int(datetime.now().timestamp())}",
            "host": platform.node(),
        }

        if self.errors is not None and len(self.errors) > 0:
            data["errors"] = [str(e) for e in self.errors]

        body = dumps(data)
        return body

    def convert_camel_case(self, string: str) -> str:
        # strip before split the sentence
        return "".join([word.capitalize() for word in string.strip().split()])

    def get_response(
        self, environ: Any | Request | None = None, scope: Any | None = None
    ) -> Response:
        return WSGIResponse(self.get_body(), self.status, self.get_headers())
