import base64
import uuid
from datetime import datetime
from random import randbytes
from threading import Thread

import pandas
from flask_pydantic import validate  # type: ignore
from pydantic import UUID4, BaseModel, Field
from pydantic_extra_types.pendulum_dt import DateTime, Duration
from sqlalchemy import func, select

from .. import app, config
from ..classes import ModelMetaData, SupportedCapabilities, TrainingInitiation
from ..controller import smart_meter_data, storage
from ..controller.training import train_model
from ..database.db_connector import create_connection
from ..exceptions.service_error import ServiceException
from ..tables import Data, Models
from ..validators import validate_meter_id


class _QueryParams(BaseModel):
    start_point: DateTime | datetime | None = Field(None, alias="startPoint")
    """The starting point for the training"""

    time_span: Duration | None = Field(None, alias="timeSpan")
    """The timespan of the training as duration"""

    weather_capability: SupportedCapabilities | None = Field(
        None, alias="weatherCapability"
    )
    """The weather capability that should be used as additional training data"""

    weather_column_name: str | None = Field(None, alias="weatherColumnName")

    comment: str | None = Field(None)


@app.put("/training/start/<meter_id>")  # type: ignore
@validate_meter_id()
@validate()
def start_model_training(meter_id: UUID4, query: _QueryParams) -> TrainingInitiation:
    training_id = base64.urlsafe_b64encode(randbytes(12)).decode(
        "utf-8"
    )  # take 12 random bytes to drop equal sign

    if query.start_point is None:
        with create_connection() as conn:
            db_query = (
                select(Data.c.date)
                .where(Data.c.meter == meter_id)
                .order_by(Data.c.date)
                .limit(1)
            )

            query.start_point = conn.execute(db_query).scalar()

    if query.time_span is not None and query.start_point is not None:
        end_point = query.start_point + query.time_span.as_timedelta()
    else:
        end_point = None

    observed_data = smart_meter_data.get_recorded_data(
        str(meter_id), query.start_point, end_point, None
    )

    metadata = ModelMetaData(
        modelId=uuid.uuid4(),
        meterId=meter_id,
        dataStartsAt=observed_data[0].time,
        dataEndsAt=observed_data[-1].time,
        comment=query.comment,
        withWeatherCapability=query.weather_capability is not None,
        weatherCapability=query.weather_capability,
        capabilityColumn=query.weather_column_name,
    )

    model_hash = metadata.generate_identifier()

    with create_connection() as conn:
        db_query = select(func.count(Models.c.hash)).where(Models.c.hash == model_hash)
        count = conn.execute(db_query).scalar_one()
        if count >= 1:
            raise ServiceException(
                "",
                409,
                "Model Already Exists",
                "The model you are trying to train already exists and cannot be retrained.",
            )

    if query.weather_capability is not None:
        if query.weather_column_name is None:
            raise ServiceException(
                "",
                400,
                "Missing Weather Column",
                "No column name sent to service even though a capability was selected",
            )

    smartmeter_data = {d.time.isoformat(): d.value for d in observed_data}

    data_series = pandas.Series(data=smartmeter_data, index=smartmeter_data.keys())

    thread = Thread(
        target=train_model,
        kwargs={
            "model_id": model_hash,
            "training_id": training_id,
            "metadata": metadata,
            "smartmeter_data": data_series,
            "weather_data": None,
        },
    )
    thread.start()
    return TrainingInitiation(modelId=model_hash, trainingId=training_id)
