from typing import Any
import isodate
from pendulum import DateTime, Duration
from psycopg.rows import dict_row
from ..classes import Datapoint
from ..database import db_connector


def get_recorded_data(
    meter_id: str,
    start_point: DateTime | None = None,
    end_point: DateTime | None = None,
    bucket_size: Duration | None = None,
) -> list[Datapoint]:
    """
    Docstring for get_recorded_data

    :param start_point: Description
    :type start_point: DateTime
    :param end_point: Description
    :type end_point: DateTime | None
    :param bucket_size: Description
    :type bucket_size: Duration | None
    :return: Description
    :rtype: list[Datapoint]
    """

    query: str = ""

    params: list[Any] = []

    if start_point is None and end_point is None and bucket_size is None:
        query = """
          SELECT value, date as ts
          FROM timeseries.water_demand_prediction
          WHERE name=%s
          ORDER BY ts ASC;
        """

        params = [meter_id]

    if start_point is None and end_point is None and bucket_size is not None:
        query = """
          SELECT sum(value) as value, time_bucket(%s, date) + %s::INTERVAL as ts
          FROM timeseries.water_demand_prediction
          WHERE name = %s
          GROUP BY ts
          ORDER BY ts ASC;
        """
        _bucket_size = isodate.duration_isoformat(bucket_size.as_timedelta())
        params = [_bucket_size, _bucket_size, meter_id]

    if start_point is None and end_point is not None and bucket_size is None:
        query = """
          SELECT value, date as ts
          FROM timeseries.water_demand_prediction
          WHERE 
            name = %s
          AND
            date < %s
          ORDER BY ts ASC;
        """
        params = [meter_id, end_point.isoformat()]

    if start_point is not None and end_point is None and bucket_size is None:
        query = """
          SELECT value, date as ts
          FROM timeseries.water_demand_prediction
          WHERE 
            name = %s
          AND
            date > %s
          ORDER BY ts ASC;
        """
        params = [meter_id, start_point.isoformat()]

    if start_point is None and end_point is not None and bucket_size is not None:
        query = """
          SELECT sum(value) as value, time_bucket(%s, date) + %s::INTERVAL as ts
          FROM timeseries.water_demand_prediction
          WHERE 
            name = %s
          AND 
            date < %s
          GROUP BY ts
          ORDER BY ts ASC;
        """
        _bucket_size = isodate.duration_isoformat(bucket_size.as_timedelta())

        params = [_bucket_size, _bucket_size, meter_id, end_point.isoformat()]

    if start_point is not None and end_point is None and bucket_size is not None:
        query = """
          SELECT sum(value) as value, time_bucket(%s, date) + %s::INTERVAL as ts
          FROM timeseries.water_demand_prediction
          WHERE 
            name = %s
          AND 
            date > %s
          GROUP BY ts
          ORDER BY ts ASC;
        """
        _bucket_size = isodate.duration_isoformat(bucket_size.as_timedelta())

        params = [_bucket_size, _bucket_size, meter_id, start_point.isoformat()]

    if start_point is not None and end_point is not None and bucket_size is None:
        query = """
          SELECT value, date as ts
          FROM timeseries.water_demand_prediction
          WHERE 
            name = %s
          AND 
            date >= %s
          AND
            date < %s
          ORDER BY ts ASC;
        """

        params = [meter_id, start_point.isoformat(), end_point.isoformat()]

    if start_point is not None and end_point is not None and bucket_size is not None:
        query = """
          SELECT sum(value) as value, time_bucket(%s, date) + %s::INTERVAL as ts
          FROM timeseries.water_demand_prediction
          WHERE 
            name = %s
          AND 
            date BETWEEN %s AND %s
          GROUP BY ts
          ORDER BY ts ASC;
        """
        _bucket_size = isodate.duration_isoformat(bucket_size.as_timedelta())

        params = [
            _bucket_size,
            _bucket_size,
            meter_id,
            start_point.isoformat(),
            end_point.isoformat(),
        ]

    with db_connector.create_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, params)

            return [
                Datapoint(time=e["ts"], value=e["value"]) for e in cursor.fetchall()
            ]
