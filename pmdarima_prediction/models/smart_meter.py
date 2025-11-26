from uuid import uuid4

from pydantic import UUID4
from sqlmodel import Field, MetaData, SQLModel


class SmartMeter(SQLModel, table=True):
    id: UUID4 = Field(default_factory=uuid4, primary_key=True)
    """The unique identifier for the smart meter"""

    name: str = Field(unique=True)
    """A human-readable name for the smart meter"""

    description: str | None = Field(default=None)
    """A human-readable description for the smart meter"""

    metadata = MetaData(schema="pmdarima")
