from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException

from .. import app
from ..exceptions import ServiceException


@app.errorhandler(Exception)
def handle_generic_exception(e: Exception) -> ResponseReturnValue:
    """Error Handler for catching all exception that occurr in a request"""
    if isinstance(e, HTTPException):
        return e

    return ServiceException(
        "",
        500,
        "Internal Service Error",
        str(e).replace("\n\t", ". ").replace("\n", ""),
        [e],
    ).get_response()
