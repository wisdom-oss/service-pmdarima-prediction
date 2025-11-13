from flask_pydantic import validate  # type: ignore
from sqlalchemy import select

from .. import app
from ..classes import SmartMeter
from ..database.db_connector import create_connection
from ..tables import Meters


@app.get("/meters")
@validate(response_many=True)
def get_meter_names() -> list[SmartMeter]:
    """
    `GET /meters`

    This method generates meter names for all Smart Meters
    """

    with create_connection() as conn:
        query = select(Meters)
        result = conn.execute(query)
        return [SmartMeter(id=i[0], name=i[1], description=i[2]) for i in result]
