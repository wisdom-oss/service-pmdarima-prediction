from functools import wraps
from typing import Any, Callable, Literal, Tuple
from uuid import UUID

from flask import Request, request
from sqlalchemy import select

from ..database.db_connector import create_connection as __open_conn
from ..exceptions import ServiceException
from ..tables import Meters


def check_meter_id(
    parameter_name: str = "meter_id",
    parameter_location: Literal["path"] | Literal["query"] | Literal["header"] = "path",
):
    """
    Check if the provided meter id is in a valid format (i.e. UUIDv4) and is present in the
    database
    """

    def _check_meter_id(f: Callable[[Any], None]):
        def __query_db(incoming_uuid: str) -> Tuple[bool, bool, str]:
            try:
                meter_id = UUID(incoming_uuid)
            except ValueError as e:
                return False, False, f"An invalid UUID as been provided. {e}"

            if meter_id.version != 4:
                return (
                    False,
                    False,
                    "The provided UUID is not of Version 4. Please check the provided UUID",
                )

            with __open_conn() as conn:
                query = select(Meters).where(Meters.c.id == meter_id)
                result = conn.execute(query)

                if result is None:
                    return (
                        False,
                        True,
                        "Received an empty result set from the database",
                    )
                return len(result.all()) == 1, False, "Unknown Smart Meter Id"

        def __check_meter_id_in_path(r: Request) -> Tuple[bool, bool, str]:
            if request.view_args is None:
                return False, True, "No path parameters available"

            raw_meter_id: str | None = request.view_args[parameter_name]
            if raw_meter_id is None:
                return (
                    False,
                    True,
                    f"No path parameter named {parameter_name} found in the view argumens.",
                )

            return __query_db(raw_meter_id)

        def __check_meter_id_in_query(r: Request) -> Tuple[bool, bool, str]:
            if request.args is None:
                return False, True, "No query parameters available"

            raw_meter_id: str | None = request.args.get(parameter_name)
            if raw_meter_id is None:
                return (
                    False,
                    True,
                    f"No query parameter named {parameter_name} found in the view argumens.",
                )

            return __query_db(raw_meter_id)

        def __check_meter_id_in_header(r: Request) -> Tuple[bool, bool, str]:
            if request.headers is None:
                return False, True, "No headers available"

            raw_meter_id: str | None = request.headers.get(parameter_name)
            if raw_meter_id is None:
                return (
                    False,
                    True,
                    f"No header named {parameter_name} found in the view argumens.",
                )

            return __query_db(raw_meter_id)

        @wraps(f)
        def __check_meter_id(*args: tuple[Any, ...], **kwargs: dict[Any, Any]):
            valid_meter, internal_error, error_message = False, False, ""

            if parameter_location == "path":
                valid_meter, internal_error, error_message = __check_meter_id_in_path(
                    request
                )
            if parameter_location == "query":
                valid_meter, internal_error, error_message = __check_meter_id_in_query(
                    request
                )
            if parameter_location == "header":
                valid_meter, internal_error, error_message = __check_meter_id_in_header(
                    request
                )

            if not valid_meter:
                raise ServiceException(
                    "",
                    500 if internal_error is True else 400,
                    "Invalid Smart Meter Id",
                    error_message,
                )

            return f(*args, **kwargs)

        return __check_meter_id

    return _check_meter_id
