from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pytz import utc


class WeatherColumn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(serialization_alias="columnName")
    """The name returned by the weather api"""

    description: str | None
    """The human-readable description of the weather column"""

    for_data_from: datetime = Field(serialization_alias="forDataFrom")
    """Data after this time has the column available"""

    for_data_until: datetime = Field(serialization_alias="forDataUntil")
    """Data before this time has the column available"""

    def __hash__(self) -> int:
        """Overridden hash method to compensate for the timezones"""
        return hash(
            {
                self.name,
                self.description,
                self.for_data_from.astimezone(utc).isoformat(),
                self.for_data_until.astimezone(utc).isoformat(),
            }
        )
