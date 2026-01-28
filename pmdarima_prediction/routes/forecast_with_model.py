import pandas
from flask_pydantic import validate
from numpy.typing import ArrayLike
from pmdarima import ARIMA
from pydantic import UUID4, BaseModel, Field
from pydantic_extra_types.pendulum_dt import Duration
from sklearn import metrics
from sqlmodel import Session, select

from .. import app
from ..controller import smart_meter_data
from ..database.db_connector import get_engine
from ..exceptions.service_error import ServiceException
from ..models import Datapoint, Prediction, TrainedModel
from ..validators import validate_model_id


class query_parameter(BaseModel):
    forecast_length: Duration = Field(Duration(days=1), alias="forecastLength")
    interval: Duration = Field(Duration(hours=1), ge=Duration(hours=1))


@app.get("/predict/<model_id>")
@validate_model_id()
@validate(response_by_alias=True)
def predict(model_id: UUID4, query: query_parameter) -> Prediction:
    with Session(get_engine()) as conn:
        db_query = select(TrainedModel).where(TrainedModel.id == model_id)
        model = conn.exec(db_query).first()
        if model is None:
            raise ServiceException(
                "",
                500,
                "Corrupted Model",
                "The model you are trying to use is corrupted or could not be found. Please retrain the model",
            )

    if model.base_data_end is None:
        raise ServiceException(
            "",
            500,
            "Model Not Usable for predictions",
            "Due to a defect in the model storage, the model cannot be used for predictions",
        )

    forecast_ends = model.base_data_end + query.forecast_length

    prediction_labels = pandas.date_range(
        start=model.base_data_end,
        end=forecast_ends,
        freq=query.interval,
        inclusive="left",
    )

    recorded_values = smart_meter_data.get_recorded_data(
        meter_id=model.meter.hex,
        start_point=prediction_labels[0].to_pydatetime(),
        end_point=prediction_labels[
            -1
        ].to_pydatetime(),  # extend the recorded data retrieval by one interval
        bucket_size=query.interval,
    )

    if len(prediction_labels) != len(recorded_values):
        raise ServiceException(
            "",
            400,
            "Prediction runs into uncheckable area",
            "The forecast cannot be validated with recorded data. Please decrease the forecast size or move the starting point further back",
        )

    prediction, confidence_intervals = model.get_model().predict(
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

    mean_absolute_error: float = metrics.mean_absolute_error(**params)

    mean_squared_error: float = metrics.mean_squared_error(**params)

    root_mean_squared_error: float = metrics.root_mean_squared_error(**params)

    r2_score = metrics.r2_score(**params)

    data_points: list[Datapoint] = []

    for i in range(len(prediction)):
        data_points.append(
            Datapoint(
                time=prediction.keys()[i].to_pydatetime(),
                value=prediction[i],
                confidence_interval=(0 if confidence_intervals[i][0] < 0 else  confidence_intervals[i][0], 0 if confidence_intervals[i][1] < 0 else confidence_intervals[i][1]),
            )
        )

    return Prediction(
        made_with_model=model_id,
        mean_absolute_error=mean_absolute_error,
        mean_squared_error=mean_squared_error,
        root_mean_squared_error=root_mean_squared_error,
        r2_score=r2_score,
        datapoints=data_points,
    )
