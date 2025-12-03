from sqlalchemy import (TIMESTAMP, UUID, Column, Float, ForeignKey, Interval,
                        MetaData, Null, PickleType, String, Table, Uuid)

__table_meta_data = MetaData(schema="pmdarima")
__timeseries_meta_data = MetaData(schema="timeseries")

Meters = Table(
    "meters",
    __table_meta_data,
    Column("id", UUID, primary_key=True),
    Column("name", String, unique=True),
    Column("description", String),
)

Models = Table(
    "models",
    __table_meta_data,
    Column("id", Uuid, primary_key=True),
    Column("hash", String, unique=True, nullable=False),
    Column("meter", ForeignKey("meters.id"), nullable=False),
    Column("comment", String),
    Column("training_start", TIMESTAMP(timezone=True)),
    Column("training_duration", Interval),
    Column("base_data_start", TIMESTAMP(timezone=True)),
    Column("base_data_end", TIMESTAMP(timezone=True)),
    Column("weather_capability", String, default=Null),
    Column("capability_column", String),
    Column("pickled_model", PickleType),
)

Data = Table(
    "water_demand_prediction",
    __timeseries_meta_data,
    Column("date", TIMESTAMP(timezone=True)),
    Column("meter", ForeignKey("pmdarima.meters.id")),
    Column("value", Float, nullable=False),
)
