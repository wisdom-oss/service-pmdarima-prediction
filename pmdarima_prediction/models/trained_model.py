import hashlib
from datetime import timedelta
from typing import cast
from uuid import uuid4

import pmdarima
from pydantic import UUID4
from pydantic_extra_types.pendulum_dt import DateTime
from sqlmodel import DateTime as sa_DateTime
from sqlmodel import Field, Interval, MetaData, PickleType, SQLModel, String

from ..weather import SupportedCapabilities


class TrainedModel(SQLModel, table=True):
    __tablename__ = "models"

    id: UUID4 = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    """The unique identifier for this model"""

    meter: UUID4 = Field(
        foreign_key="meters.id",
        nullable=False,
    )
    """The ID of the SmartMeter that provided the data for the training of this model"""

    hash: str = Field(
        unique=True,
        nullable=False,
    )
    """The hash of the model to check for other models having the same training parameters"""

    comment: str | None = Field(
        nullable=True,
    )
    """An optional comment about the model"""

    training_start: DateTime = Field(
        schema_extra={
            "serialization_alias": "trainingStart"
        },  # todo: switch to alias= as soon as pr #1577 of fastapi/sqlmodel is merged
        sa_type=sa_DateTime(timezone=True),
    )
    """The date and time (accompanied by a timezone) at which the training of the model started"""

    training_duration: timedelta = Field(
        schema_extra={
            "serialization_alias": "trainingDuration"
        },  # todo: switch to alias= as soon as pr #1577 of fastapi/sqlmodel is merged
        sa_type=Interval,
    )
    """The duration it took to train this model"""

    base_data_start: DateTime = Field(
        schema_extra={
            "serialization_alias": "dataStartsAt"
        },  # todo: switch to alias= as soon as pr #1577 of fastapi/sqlmodel is merged
        sa_type=sa_DateTime(timezone=True),
    )
    """The start of the data used to train this model"""

    base_data_end: DateTime = Field(
        schema_extra={
            "serialization_alias": "dataEndsAt"
        },  # todo: switch to alias= as soon as pr #1577 of fastapi/sqlmodel is merged
        sa_type=sa_DateTime(timezone=True),
    )
    """The last timestamp of the dataset used to train this model"""

    weather_capability: SupportedCapabilities | None = Field(
        schema_extra={
            "serialization_alias": "weatherCapability"
        },  # todo: switch to alias= as soon as pr #1577 of fastapi/sqlmodel is merged
        sa_type=String,
        default=None,
    )
    """An optional weather capability that has been used as exogenous data for training the model"""

    capability_column: str | None = Field(
        schema_extra={
            "serialization_alias": "capabilityColumn"
        },  # todo: switch to alias= as soon as pr #1577 of fastapi/sqlmodel is merged
        default=None,
    )
    """The column of the weather capability that has been used for the generation of exogenous data for training the model"""

    pickled_model: object | None = Field(
        sa_type=PickleType,
        default=None,
        exclude=True,
    )
    """The trained model. Please use `.get_model()` to retrieve a corretly typed model"""

    metadata = MetaData(schema="pmdarima")

    def get_model(self) -> pmdarima.ARIMA:
        if self.pickled_model is None:
            raise ValueError("no model available")
        return cast(pmdarima.ARIMA, self.pickled_model)

    def __plain_hash(self) -> str:
        """Generate a plaintext hash which uniquely identifies the model"""
        return hashlib.md5(
            bytes(
                self.model_dump_json(
                    exclude=set(["id", "training_time", "trained_at", "pickled_model"])
                ),
                "utf-8",
            ),
            usedforsecurity=False,
        ).hexdigest()
