from __main__ import app

from flask import make_response
import pendulum
import psycopg
from psycopg.rows import dict_row

from classes import Datapoint
from flask_pydantic import validate
from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import Duration, DateTime

from database import db_connector
from exceptions.service_error import ServiceException

from validators import validate_meter_id


class queryParameter(BaseModel):
    bucket_size: Duration | None = None
    start: DateTime = pendulum.datetime(1, 1, 1, 0, 0, 0, 0) # create the first possible date
    end: DateTime = pendulum.now() # use the current datetime as upper limit


@app.get("/measured-data/<meter_id>")
@validate_meter_id()
@validate(response_many=True)
def get_measured_data(
    meter_id: str, query: queryParameter
) -> list[Datapoint]:
    """
    Docstring for get_single_smart_meter_data

    :param query: Description
    :type query: queryParameter
    :return: Description
    :rtype: list[Any]
    """

    if query.start > query.end:
        raise ServiceException(
            "",
            400,
            "DateTime Range Boundaray Error",
            "The requested start point for the timeseries is after the requested end or the current time",
        )

    datapoints: list[Datapoint] = list()

    with db_connector.create_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            if query.bucket_size is None:
                cursor.execute(
                    """
                  SELECT value, date as ts
                  FROM timeseries.water_demand_prediction 
                  WHERE
                      name=%s
                    AND 
                      date BETWEEN %s AND %s
                  ORDER BY ts ASC;
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
                  SELECT sum(value) as value, time_bucket(%s, date) + %s::INTERVAL as ts
                  FROM timeseries.water_demand_prediction
                  WHERE 
                      name=%s
                    AND 
                      date BETWEEN %s AND %s
                  GROUP BY ts
                  ORDER BY ts ASC;
                  """,
                    (
                        query.bucket_size.to_iso8601_string(),
                        query.bucket_size.to_iso8601_string(),
                        meter_id,
                        query.start.isoformat(),
                        query.end.isoformat(),
                    ),
                )

            entries = cursor.fetchall()

            datapoints = [Datapoint(time=e["ts"], value=e["value"]) for e in entries]

    return datapoints
