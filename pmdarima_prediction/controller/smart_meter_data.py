from typing import Any

import isodate
from pendulum import DateTime, Duration
from sqlalchemy import Select, TextClause, func, select, text
from sqlalchemy.sql.operators import and_

from ..database import db_connector
from ..models import Datapoint
from ..tables import Data


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
    query: TextClause | Select[Any] | None = None
    params: dict[str, Any] = {}

    if start_point is None and end_point is None and bucket_size is None:
        query = select(Data).where(Data.c.meter == meter_id)

    if start_point is None and end_point is None and bucket_size is not None:
        query = text("""
        SELECT time_bucket(:bucket_size, date) + :bucket_size ::INTERVAL as ts, sum(value) as value
          FROM timeseries.water_demand_prediction
          WHERE meter = :meter_id
          GROUP BY ts
          ORDER BY ts ASC;
        """)
        _bucket_size = isodate.duration_isoformat(bucket_size.as_timedelta())
        params = {"bucket_size": _bucket_size, "meter_id": meter_id}

    if start_point is None and end_point is not None and bucket_size is None:
        query = select(Data).where(
            and_(
                Data.c.meter == meter_id,
                Data.c.date < end_point,
            )
        )

    if start_point is not None and end_point is None and bucket_size is None:
        query = select(Data).where(
            and_(
                Data.c.meter == meter_id,
                Data.c.date >= start_point,
            )
        )

    if start_point is None and end_point is not None and bucket_size is not None:
        query = text("""
        SELECT time_bucket(:bucket_size, date) + :bucket_size ::INTERVAL as date, sum(value) as value
          FROM timeseries.water_demand_prediction
          WHERE
            meter = :meter_id
          AND
            date < :end_date
          GROUP BY ts
          ORDER BY ts ASC;
        """)
        _bucket_size = isodate.duration_isoformat(bucket_size.as_timedelta())
        params = {
            "bucket_size": _bucket_size,
            "meter_id": meter_id,
            "end_date": end_point,
        }

    if start_point is not None and end_point is None and bucket_size is not None:
        query = text("""
          SELECT time_bucket(:bucket_size, date) + :bucket_size ::INTERVAL as date, sum(value) as value
          FROM timeseries.water_demand_prediction
          WHERE
            meter = :meter_id
          AND
            date >= :start_date
          GROUP BY ts
          ORDER BY ts ASC;
        """)
        _bucket_size = isodate.duration_isoformat(bucket_size.as_timedelta())

        params = {
            "bucket_size": _bucket_size,
            "meter_id": meter_id,
            "start_date": start_point,
        }

    if start_point is not None and end_point is not None and bucket_size is None:
        query = select(Data).where(
            and_(
                and_(
                    Data.c.meter == meter_id,
                    Data.c.date < end_point,
                ),
                Data.c.date >= start_point,
            )
        )

    if start_point is not None and end_point is not None and bucket_size is not None:
        query = text("""
          SELECT (time_bucket(:bucket_size, date) + :bucket_size) as ts, sum(value) as value
          FROM timeseries.water_demand_prediction
          WHERE
            meter = :meter_id
          AND
            date >= :start_date
          AND
            date <= :end_date
          GROUP BY ts
          ORDER BY ts ASC;
        """)
        params = {
            "bucket_size": bucket_size,
            "meter_id": meter_id,
            "start_date": start_point,
            "end_date": end_point,
        }

    if query is None:
        raise ValueError("unable to query with nonexistent query")
    with db_connector.create_connection() as conn:
        result = conn.execute(query, params if isinstance(query, TextClause) else None)
        return [
            Datapoint(time=(e["date"] if "ts" not in e else e["ts"]), value=e["value"])
            for e in result.mappings().all()
        ]
