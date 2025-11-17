import pandas
from flask_pydantic import validate
from numpy.typing import ArrayLike
from pmdarima import ARIMA
from pydantic import BaseModel, Field
from pydantic_extra_types.pendulum_dt import Duration
from sklearn import metrics
from sqlalchemy import select

from .. import app
from ..classes import ConfidenceDatapoint, ModelMetaData, Prediction
from ..controller import smart_meter_data, storage
from ..database.db_connector import create_connection
from ..exceptions.service_error import ServiceException
from ..tables import Models
from ..validators import validate_model_id


class query_parameter(BaseModel):
    forecast_length: Duration = Field(Duration(days=1), alias="forecastLength")
    interval: Duration = Field(Duration(hours=1))


@app.get("/predict/<model_id>")
@validate_model_id()
@validate(response_by_alias=True)
def predict(model_id: str, query: query_parameter) -> Prediction:
    with create_connection() as conn:
        db_query = select(Models).where(Models.c.id == model_id).limit(1)
        result = conn.execute(db_query).mappings().fetchall()[0]

    model_meta = ModelMetaData(
        modelId=result["id"],
        meterId=result["meter"],
        dataStartsAt=result["base_data_start"],
        dataEndsAt=result["base_data_end"],
    )

    if model_meta.end_point is None:
        raise ServiceException(
            "",
            500,
            "Model Not Usable for predictions",
            "Due to a defect in the model storage, the model cannot be used for predictions",
        )

    forecast_ends = model_meta.end_point + query.forecast_length

    prediction_labels = pandas.date_range(
        start=model_meta.end_point,
        end=forecast_ends,
        freq=query.interval,
        inclusive="right",
    )

    recorded_values = smart_meter_data.get_recorded_data(
        meter_id=model_meta.for_meter.hex,
        start_point=prediction_labels[0].to_pydatetime(),
        end_point=prediction_labels[-1].to_pydatetime()
        + query.interval,  # extend the recorded data retrieval by one interval
    )

    if len(prediction_labels) != len(recorded_values):
        raise ServiceException(
            "",
            400,
            "Prediction runs into uncheckable area",
            "The forecast cannot be validated with recorded data. Please decrease the forecast size or move the starting point further back",
        )

    model: ARIMA = result["pickled_model"]
    prediction, confidence_intervals = model.predict(
        n_periods=len(prediction_labels), return_conf_int=True, alpha=0.1
    )

    if not isinstance(prediction, pandas.Series):
        raise ServiceException(
            "",
            500,
            "Unexcpected Return Type",
            "The prediction returned by ARIMA is not in the required type",
        )

    params: dict[str, ArrayLike] = {
        "y_true": [e.value for e in recorded_values],
        "y_pred": prediction,
    }

    mean_absolute_error = metrics.mean_absolute_error(**params)

    mean_squared_error = metrics.mean_squared_error(**params)

    root_mean_squared_error = metrics.root_mean_squared_error(**params)

    r2_score = metrics.r2_score(**params)

    data_points: list[ConfidenceDatapoint] = []

    for i in range(len(prediction)):
        data_points.append(
            ConfidenceDatapoint(
                time=prediction.keys()[i].to_pydatetime(),
                value=prediction[i],
                confidenceInterval=confidence_intervals[i],
            )
        )

    return Prediction(
        madeWithModel=model_id,
        mae=mean_absolute_error,
        mse=mean_squared_error,
        rmse=root_mean_squared_error,
        r2=r2_score,
        datapoints=data_points,
    )
