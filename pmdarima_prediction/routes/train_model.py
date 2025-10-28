import base64
from datetime import datetime
from random import randbytes
from threading import Thread

import pandas
from flask_pydantic import validate  # type: ignore
from pydantic import BaseModel, Field
from pydantic_extra_types.pendulum_dt import DateTime, Duration

from .. import app, config
from ..classes import ModelMetaData, SupportedCapabilities
from ..controller import smart_meter_data, storage
from ..controller.training import train_model
from ..database import db_connector
from ..exceptions.service_error import ServiceException
from ..validators import validate_meter_id
from ..weather import API as weather_api


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


@app.get("/training/start/<meter_id>") # type: ignore
@validate_meter_id()
@validate()
def start_model_training(meter_id: str, query: _QueryParams):
    training_id = base64.urlsafe_b64encode(randbytes(12)).decode(
        "utf-8"
    )  # take 12 random bytes to drop equal sign

    if query.start_point is None:
        with db_connector.create_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT date
                    FROM timeseries.water_demand_prediction
                    WHERE name=%s
                    ORDER BY date ASC
                    LIMIT 1; 
                    """,
                    [meter_id],
                )

                results = cursor.fetchone()
                if results is not None:
                    if not isinstance(results[0], datetime):
                        raise ServiceException(
                            "",
                            500,
                            "Unable to determine start point automatically",
                            "The service is unable to determine the start point for the model training. Please specify it manually",
                        )
                    query.start_point = results[0]
                else:
                    raise ServiceException(
                        "",
                        500,
                        "Unable to determine start point automatically",
                        "The service is unable to determine the start point for the model training. Please specify it manually",
                    )

    metadata = ModelMetaData(
        meter=meter_id,
        startingPoint=query.start_point,
        timeSpan=query.time_span,
        withWheaterCapability=query.weather_capability is not None,
        weatherCapability=query.weather_capability,
        columnName=query.weather_column_name,
    )

    model_id = metadata.generate_identifier()

    if storage.model_exists(model_id) and not config.allow_overwriting_models:
        raise ServiceException(
            "",
            409,
            "Model Overwriting not Allowed",
            "The current configuration of the service does not allow for overwriting already existing models. Please train a new model with different parameters",
        )

    if query.time_span is not None:
        end_point = query.start_point + query.time_span.as_timedelta()
    else:
        end_point = None

    observed_data = smart_meter_data.get_recorded_data(
        meter_id, metadata.start_point, end_point, None
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
            "model_id": model_id,
            "training_id": training_id,
            "metadata": metadata,
            "smartmeter_data": data_series,
            "weather_data": None,
        },
    )
    thread.start()
    return {"modelID": model_id, "trainingID": training_id}
