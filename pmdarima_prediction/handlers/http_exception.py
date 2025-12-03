from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException

from .. import app
from ..exceptions import ServiceException


@app.errorhandler(HTTPException)
def handle_http_exception(e: HTTPException) -> ResponseReturnValue:
    """Error Handler for catching all exception that occurr in a request"""
    return ServiceException(
        "",
        e.code if e.code is not None else 500,
        e.name,
        e.description if e.description is not None else "",
        [e],
    ).get_response()
