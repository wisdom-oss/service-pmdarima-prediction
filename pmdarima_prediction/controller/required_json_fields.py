from functools import wraps
from flask import request
import typing
from interfaces import ServiceError


# type: ignore
def require_json_fields_not_null(*requiredKeys: str):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if not request.is_json:
                raise ServiceError(
                    "",
                    415,
                    "JSON Request Body Expected",
                    "The request did not contain a JSON parseable body",
                    [],
                )

            data = request.get_json(silent=True)
            if not data or data is None:
                return fn(*args, **kwargs)

            exceptions: list[Exception] = []
            for requiredKey in requiredKeys:
                if requiredKey not in data.keys():
                    exceptions.append(
                        Exception(
                            f"The required field '{requiredKey}' is not present in the request body"
                        )
                    )
                    continue

                if data.get(requiredKey) == None:
                    exceptions.append(
                        Exception(
                            f"The requried field '{requiredKey} contains a null value"
                        )
                    )

            if len(exceptions) != 0:
                raise ServiceError(
                    "",
                    400,
                    "Required JSON Field Constraint Violated",
                    "At least one required JSON filed is null or not present in the request body. Please check the errors for more details",
                    exceptions,
                )
            return fn(*args, **kwargs)

        return decorator

    return wrapper
