from __main__ import app
from datetime import datetime
from random import randbytes, randint
from flask_pydantic import validate
from pydantic_extra_types.pendulum_dt import Duration, DateTime
from pydantic import BaseModel, Field
from sys import maxsize
from validators import validate_meter_id
import base64

from classes import ModelMetadata, SupportedCapabilities

class requestBody(BaseModel):

  start_point: DateTime = Field(alias="startPoint")
  """The starting point for the training"""

  time_span: Duration | None = Field(None, alias="timeSpan")
  """The timespan of the training as duration"""

  weather_capability: SupportedCapabilities | None = Field(None, alias="weatherCapability")
  """The weather capability that should be used as additional training data"""

  weather_column_name: str | None = Field(None, alias="weatherColumnName")


@app.get("/training/status/<training_id>")
@validate()
def start_model_training(training_id: str):

 
  return training_id