from pydantic import UUID4, BaseModel, Field

from .datapoint import Datapoint


class Prediction(BaseModel):
    made_with_model: UUID4 = Field(serialization_alias="madeWithModel")
    """The UUID of the model used to make the prediction"""

    datapoints: list[Datapoint]
    mean_absolute_error: float = Field(serialization_alias="mae")
    mean_squared_error: float = Field(serialization_alias="mse")
    root_mean_squared_error: float = Field(serialization_alias="rmse")
    r2_score: float = Field(serialization_alias="r2")
