from functools import wraps
from flask import jsonify, request
from interfaces import ServiceError

def check_for_empty_json_fields(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.json
        if not data:
            raise ServiceError("", 400, "Bad Request", "JSON Request Body Missing", [])

        # Check if any value is None
        exceptions: list[Exception] = []
        for key, value in data.items():
            if value == None:
                exceptions.append(Exception(f"The field '{key}' contained 'null' as value"))

        if len(exceptions) != 0:
            raise ServiceError("", 400, "Bad Request", f"At least one field in the request body contains a 'null' value", exceptions)

        return f(*args, **kwargs)
    return decorated_function