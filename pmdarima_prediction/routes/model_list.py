from flask_pydantic import validate  # type: ignore
from sqlmodel import Session, select

from .. import app
from ..database import db_connector
from ..models import TrainedModel


@app.get("/models")
@validate(response_many=True, response_by_alias=True)
def get_trained_models() -> list[TrainedModel]:
    with Session(db_connector.get_engine()) as db:
        query = select(
            TrainedModel.id,
            TrainedModel.meter,
            TrainedModel.hash,
            TrainedModel.comment,
            TrainedModel.training_start,
            TrainedModel.training_duration,
            TrainedModel.base_data_start,
            TrainedModel.base_data_end,
            TrainedModel.weather_capability,
            TrainedModel.capability_column,
        )

        result = db.exec(query)
        models = result.all()
        return [TrainedModel.model_validate(m) for m in models]
