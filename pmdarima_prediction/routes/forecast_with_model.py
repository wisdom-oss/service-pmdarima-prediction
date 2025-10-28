from .. import app

from flask_pydantic import validate
import pandas
from pydantic import BaseModel, Field
from pydantic_extra_types.pendulum_dt import Duration
from sklearn import metrics


from ..classes import ConfidenceDatapoint, Prediction
from ..controller import smart_meter_data, storage
from ..exceptions.service_error import ServiceException


class query_parameter(BaseModel):
    forecast_length: Duration = Field(Duration(days=1))
    interval: Duration = Field(Duration(hours=1))


@app.get("/predict/<model_id>")
@validate(response_by_alias=True)
def predict(model_id: str, query: query_parameter) -> Prediction:
    model_meta = storage.load_metdata_for_model(model_id)
    if model_meta.time_span is None:
        raise ServiceException(
            "",
            500,
            "Stored Model Defect",
            "The stored model has a defect and cannot be used for predictions. Please delete the model, retrain it and try again",
        )

    model_ends = model_meta.start_point + model_meta.time_span
    forecast_ends = model_ends + query.forecast_length

    prediction_labels = pandas.date_range(
        start=model_ends, end=forecast_ends, freq=query.interval, inclusive="right"
    )

    recorded_values = smart_meter_data.get_recorded_data(
        meter_id=model_meta.for_meter,
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

    model = storage.load_model_by_id(model_id)
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

    mean_absolute_error = metrics.mean_absolute_error(
        y_true=[e.value for e in recorded_values],
        y_pred=prediction,
    )

    mean_squared_error = metrics.mean_squared_error(
        y_true=[e.value for e in recorded_values],
        y_pred=prediction,
    )

    root_mean_squared_error = metrics.root_mean_squared_error(
        y_true=[e.value for e in recorded_values],
        y_pred=prediction,
    )

    r2_score = metrics.r2_score(
        y_true=[e.value for e in recorded_values],
        y_pred=prediction,
    )

    datapoints: list[ConfidenceDatapoint] = []

    for i in range(len(prediction)):
        datapoints.append(
            ConfidenceDatapoint(
                time=prediction.keys()[i].to_pydatetime(),
                value=prediction[i],
                confidence_interval=confidence_intervals[i],
            )
        )

    return Prediction(
        madeWithModel=model_id,
        mae=mean_absolute_error,
        mse=mean_squared_error,
        rmse=root_mean_squared_error,
        r2=r2_score,
        datapoints=datapoints,
    )
