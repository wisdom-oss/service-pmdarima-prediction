from flask.typing import ResponseReturnValue

from .. import app
from ..exceptions import ServiceException


@app.errorhandler(ServiceException)
def handle_service_exception(e: ServiceException) -> ResponseReturnValue:
    """Error Handler for catching"""
    return e.get_response()
