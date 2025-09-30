from __main__ import app

import pendulum

from classes import Datapoint
from flask_pydantic import validate
from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import Duration, DateTime

from database import db_connector
from exceptions.service_error import ServiceException


class queryParameter(BaseModel):
    bucket_size: Duration | None = None
    start: DateTime = pendulum.datetime(1, 1, 1, 0, 0, 0, 0)
    end: DateTime = pendulum.now()


@app.get("/single-meter/<meter_id>")
@validate(response_many=True)
def get_single_smart_meter_data(
    meter_id: str, query: queryParameter
) -> list[Datapoint]:
    """
    Docstring for get_single_smart_meter_data

    :param query: Description
    :type query: queryParameter
    :return: Description
    :rtype: list[Any]
    """

    # validate that the provided smart meter id is available in the
    # database
    with db_connector.create_connection() as conn:
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

    if query.start > query.end:
        raise ServiceException(
            "",
            400,
            "DateTime Range Boundaray Error",
            "The requested start point for the timeseries is after the requested end or the current time",
        )

    datapoints: list[Datapoint] = list()

    with db_connector.create_connection() as conn:
        with conn.cursor() as cursor:
            if query.bucket_size is None:
                cursor.execute(
                    """
                  SELECT value, date 
                  FROM timeseries.water_demand_prediction 
                  WHERE
                      name=%s
                    AND 
                      date BETWEEN %s AND %s;
                  """,
                    (
                        meter_id,
                        query.start.isoformat(),
                        query.end.isoformat(),
                    ),
                )
            else:
                cursor.execute(
                    """
                  SELECT sum(value), time_bucket(%s, date) as bucket
                  FROM timeseries.water_demand_prediction
                  WHERE 
                      name=%s
                    AND 
                      date BETWEEN %s AND %s
                  GROUP BY bucket
                  ORDER BY bucket ASC;
                  """,
                    (
                        query.bucket_size.to_iso8601_string(),
                        meter_id,
                        query.start.isoformat(),
                        query.end.isoformat(),
                    ),
                )

            entries = cursor.fetchall()

            datapoints = [Datapoint(time=e[1], value=e[0]) for e in entries]

    return datapoints
