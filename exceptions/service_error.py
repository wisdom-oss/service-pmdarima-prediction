from werkzeug.exceptions import HTTPException
from werkzeug.sansio.response import Response
from werkzeug.wrappers.request import Request
from werkzeug.wrappers.response import Response as WSGIResponse
from typing import Any
from platform import node
from datetime import datetime
from traceback import format_exception
from flask import json


class ServiceException(HTTPException):
    """
    Docstring for ServiceException
    """

    _type: str
    """
    The "type" member is a JSON string containing a URI reference that identifies
    the problem type.
    Consumers MUST use the "type" URI (after resolution, if necessary) as the 
    problem type's primary identifier.
    """

    _status: int
    """
    The status code the error will be retuned with.
    This will always be the same code output by Flask to let HTTP software know
    the correct status code, while displaying it for consumer convenicene
    """

    _title: str
    """
    A short, human-readable summary of the problem type.
    It should not change from occurrence to occurrence of a ServiceException.
    """

    _detail: str
    """
    The human-readable explanation for the occurrence of the error.
    This explanation should help with correcting the error instead of offering
    debugging advice.
    """

    _errors: list[Exception] | None
    """
    A list of Exceptions that should be converted into stacktraces and sent back
    to accompany the error with more technical details
    """

    _instance: str
    """
    A unqiue URI tag that identifies the execption and allows revisiting this
    error inside logfiles.
    """

    _host: str
    """
    The host on which the error originated
    """

    __risen_at: datetime
    """
    The datetime at which the error was raised
    """

    def __init__(
        self,
        type: str,
        status: int,
        title: str,
        details: str,
        errors: list[Exception] | None = None,
    ) -> None:
        """
        Create a new ServiceException

        :param type: A URI identifying the problem type
        :type type: str
        :param status: The HTTP status code that should be sent back to the client
        :type status: int
        :param title: A short title which summarizes the exception
        :type title: str
        :param details: A human-readable text which describes the problem while
                        foucusing on problem correction instead of debugging
        :type details: str
        :param errors: A list of exceptions that will be sent back to the client
                       to help with debugging.
        :type errors: list[Exception] | None

        :raises ValueError: A value did not conform to the constraints put on by
                            the class
        """
        self.__risen_at = datetime.now()
        if type.strip() == "":
            self._type = "https://werkzeug.palletsprojects.com/en/stable/exceptions/#werkzeug.exceptions.HTTPException"
        else:
            self._type = type.strip()

        if status < 0 or status > 599:
            raise ValueError(
                "HTTP Status Codes may not exceed 599 or be in the negative area"
            )
        self._status = status

        if title.strip() == "":
            raise ValueError("The title of the ServiceException may not be empty")
        self._title = title.strip()

        self._detail = details.strip()
        self._errors = errors

        self._host = node()
        self._instance = f"tag:{self._host},{self.__risen_at.strftime("%Y-%m-%d")}:{self._title.title().replace(" ", "")}:{int(self.__risen_at.timestamp())}"

    def get_headers(
        self, environ: dict[str, Any] | None = None, scope: dict[str, Any] | None = None
    ) -> list[tuple[str, str]]:
        """
        Get the list of headers for responding with this Exception 
        """
        return [("Content-Type", "application/problem+json; charset=utf-8")]
    
    def get_body(self, environ: dict[str, Any] | None = None, scope: dict[str, Any] | None = None) -> str:
        """
        Format the ServiceException into a response body
        """
        responseBody: dict[str, Any] = {
            "type": self._type.strip(),
            "status": self._status,
            "title": self._title.strip(),
            "detail": self._detail.strip(),
            "instance": self._instance,
            "host": self._host
        }
        
        if self._errors is not None and len(self._errors) > 0:
          stacktraces: list[str] = []  
          for error in self._errors:
              stacktrace = format_exception(error)
              stacktraces.append("\n".join(stacktrace))

          responseBody["errors"] = stacktraces

        return json.dumps(responseBody)
    
    def get_response(self, environ: Any | Request | None = None, scope: dict[str, Any] | None = None) -> Response:
        return WSGIResponse(self.get_body(), self._status, self.get_headers())
