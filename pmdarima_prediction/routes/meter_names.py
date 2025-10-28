from .. import app
from ..database.db_connector import create_connection
from ..classes import SmartMeter
from flask_pydantic import validate # type: ignore


@app.get("/meter-names")
@validate(response_many=True)
def get_meter_names() -> list[SmartMeter]:
    """
    `GET /meter-names`

    This method generates meter names for all Smart Meters
    """

    with create_connection() as db:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT name FROM timeseries.water_demand_prediction"
            )
            result = cursor.fetchall()
            return [
                SmartMeter(id=i[0], name=" ".join(i[0].split("-")).title())
                for i in result
            ]
