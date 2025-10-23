from functools import wraps
from typing import Any, Callable
from flask import request
from exceptions.service_error import ServiceException
from database.db_connector import create_connection as __open_conn


def validate_meter_id(parameter_name: str = "meter_id"):
  """
  Validate that the meter id is set and that the meter id is available in the
  database.
  If the `view_args` on the incoming request are empty the request is just being
  passed trough.
  
  :param parameter_name: The name of the path parameter containing the meter id (defaults to `meter_id`)
  :type parameter_name: str
  """
  def _validate_meter_id(f: Callable[[Any], None]):
    @wraps(f)
    def __validate_meter_id(*args: tuple[Any,...], **kwargs: dict[Any, Any]):
      if request.view_args is None:
        return f(*args, **kwargs)
      
      meter_id: str | None = request.view_args["meter_id"]
      if meter_id is None:
        raise ServiceException(
            "",
            400,
            "Missing Smart Meter ID",
            "No smart meter id has been provided even though the path requires it",
        ) 
      
      with __open_conn() as conn:
          with conn.cursor() as cursor:
              cursor.execute(
                  "SELECT DISTINCT name FROM timeseries.water_demand_prediction WHERE name=%s",
                  (meter_id,),
              )
              results = cursor.fetchall()
              found_ids = [r[0] for r in results]

              if meter_id not in found_ids:
                  raise ServiceException(
                      "",
                      404,
                      "Unknown Smart Meter ID",
                      "The provided smart meter does not exist",
                  )
              
      return f(*args, **kwargs)
    return __validate_meter_id
  return _validate_meter_id