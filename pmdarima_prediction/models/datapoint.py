from datetime import datetime
from typing import Tuple

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Datapoint(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    time: datetime
    value: int | float
    confidence_interval: Tuple[float, float] | None = Field(
        default=None,
        serialization_alias="confidenceInterval",
    )
