from flask_pydantic import validate  # type: ignore
from sqlalchemy import select

from .. import app
from ..classes import ModelMetaData
from ..database import db_connector
from ..tables import Models


@app.get("/models")
@validate(response_many=True, response_by_alias=True)
def get_trained_models() -> list[ModelMetaData]:
    with db_connector.create_connection() as db:
        query = select(
            Models.c.id,
            Models.c.meter,
            Models.c.comment,
            Models.c.training_start,
            Models.c.training_duration,
            Models.c.base_data_start,
            Models.c.base_data_end,
            Models.c.weather_capability,
            Models.c.capability_column,
        )

        result = db.execute(query)
        return [
            ModelMetaData(
                modelId=r["id"],
                meterId=r["meter"],
                comment=r["comment"],
                trainedAt=r["training_start"],
                trainingTime=r["training_duration"],
                dataStartsAt=r["base_data_start"],
                dataEndsAt=r["base_data_end"],
                withWeatherCapability=r["weather_capability"] is not None,
                weatherCapability=r["weather_capability"],
                capabilityColumn=r["capability_column"],
            )
            for r in result.mappings().all()
        ]
