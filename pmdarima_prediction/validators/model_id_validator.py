from functools import wraps
from typing import Any, Callable, Literal, Tuple
from uuid import UUID

from flask import Request, request
from sqlalchemy import select

from ..database.db_connector import create_connection as __open_conn
from ..exceptions import ServiceException
from ..tables import Models


def check_model_id(
    parameter_name: str = "model_id",
    parameter_location: Literal["path"] | Literal["query"] | Literal["header"] = "path",
):
    def _check_model_id(f: Callable[[Any], None]):
        def __query_db(incoming_uuid: str) -> Tuple[bool, bool, str]:
            try:
                model_id = UUID(incoming_uuid)
            except ValueError as e:
                return False, False, f"An invalid UUID as been provided. {e}"

            if model_id.version != 4:
                return (
                    False,
                    False,
                    "The provided UUID is not of Version 4. Please check the provided UUID",
                )

            with __open_conn() as conn:
                query = select(Models.c.id).where(Models.c.id == model_id)
                result = conn.execute(query)
                if result is None:
                    return (
                        False,
                        True,
                        "Received an empty result set from the database",
                    )
                return len(result.all()) == 1, False, "Unknown Model Id"

        def __check_model_id_in_path(r: Request) -> Tuple[bool, bool, str]:
            if request.view_args is None:
                return False, True, "No path parameters available"

            raw_model_id: str | None = request.view_args[parameter_name]
            if raw_model_id is None:
                return (
                    False,
                    True,
                    f"No path parameter named {parameter_name} found in the view argumens.",
                )

            return __query_db(raw_model_id)

        def __check_model_id_in_query(r: Request) -> Tuple[bool, bool, str]:
            if request.args is None:
                return False, True, "No query parameters available"

            raw_model_id: str | None = request.args.get(parameter_name)
            if raw_model_id is None:
                return (
                    False,
                    True,
                    f"No query parameter named {parameter_name} found in the view argumens.",
                )

            return __query_db(raw_model_id)

        def __check_model_id_in_header(r: Request) -> Tuple[bool, bool, str]:
            if request.headers is None:
                return False, True, "No headers available"

            raw_model_id: str | None = request.headers.get(parameter_name)
            if raw_model_id is None:
                return (
                    False,
                    True,
                    f"No header named {parameter_name} found in the view argumens.",
                )

            return __query_db(raw_model_id)

        @wraps(f)
        def __check_model_id(*args: tuple[Any, ...], **kwargs: dict[Any, Any]):
            if parameter_location not in ["path", "query", "header"]:
                raise ServiceException(
                    "",
                    500,
                    "Model Id Validator Configuration Invalid",
                    "The configuration specifies a unknown parameter location",
                )

            valid_model_id, internal_error, error_message = False, False, ""

            if parameter_location == "path":
                valid_model_id, internal_error, error_message = (
                    __check_model_id_in_path(request)
                )
            if parameter_location == "query":
                valid_model_id, internal_error, error_message = (
                    __check_model_id_in_query(request)
                )
            if parameter_location == "header":
                valid_model_id, internal_error, error_message = (
                    __check_model_id_in_header(request)
                )

            if not valid_model_id:
                raise ServiceException(
                    "",
                    500 if internal_error is True else 400,
                    "Invalid Model Id",
                    error_message,
                )

            return f(*args, **kwargs)

        return __check_model_id

    return _check_model_id
