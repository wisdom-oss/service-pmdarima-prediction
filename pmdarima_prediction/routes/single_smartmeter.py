from flask_pydantic import validate  # type: ignore
from pydantic import BaseModel, Field
from pydantic_extra_types.pendulum_dt import DateTime, Duration

from .. import app
from ..classes import Datapoint
from ..controller import smart_meter_data
from ..exceptions.service_error import ServiceException
from ..validators import validate_meter_id


class _QueryParams(BaseModel):
    bucket_size: Duration | None = Field(None, alias="bucketSize")
    start: DateTime | None = None  # create the first possible date
    end: DateTime | None = None  # use the current datetime as upper limit


@app.get("/measured-data/<meter_id>") # type: ignore
@validate_meter_id() 
@validate(response_many=True)
def get_measured_data(meter_id: str, query: _QueryParams) -> list[Datapoint]:
    """
    GET /measured-data/:meter_id

    Get the measured data points
    """
    if (query.start is not None and query.end is not None) and query.start > query.end:
        raise ServiceException(
            "",
            400,
            "DateTime Range Boundary Error",
            "The requested start point for the timeseries is after the requested end or the current time",
        )

    return smart_meter_data.get_recorded_data(
        meter_id, query.start, query.end, query.bucket_size
    )
