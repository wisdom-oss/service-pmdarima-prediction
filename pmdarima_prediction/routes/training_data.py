from pydantic import UUID4
from sqlmodel import Session, select
from flask_pydantic import validate # type: ignore

from .. import app
from ..controller import smart_meter_data
from ..database.db_connector import get_engine
from ..exceptions.service_error import ServiceException
from ..models import Datapoint, TrainedModel
from ..validators import validate_model_id


@app.get("/models/<model_id>/training-data") # type: ignore
@validate_model_id()
@validate(response_many=True, response_by_alias=True)
def get_training_dataset(model_id: UUID4) -> list[Datapoint]:
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

    return smart_meter_data.get_recorded_data(
        str(model.meter),
        model.base_data_start,
        model.base_data_end,
    )
