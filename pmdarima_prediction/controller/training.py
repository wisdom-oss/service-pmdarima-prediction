import logging
import warnings
from contextlib import redirect_stdout
from datetime import datetime
from os import path
from time import time

import pandas as pd
import pmdarima as pmd
from pydantic_extra_types.pendulum_dt import Duration
from sqlalchemy import insert

from .. import config
from ..classes import ModelMetaData
from ..database.db_connector import create_connection
from ..tables import Models

warnings.simplefilter(action="ignore", category=FutureWarning)


def train_model(
    model_id: str,
    training_id: str,
    metadata: ModelMetaData,
    smartmeter_data: pd.Series,
    weather_data: pd.Series | None,
) -> None:
    training_log = path.join(config.log_storage_location, f"{training_id}.log")
    with open(training_log, "w", buffering=1) as f:
        with redirect_stdout(f):
            print(f"initializing training for model {model_id}")

            first_differencing_order = pmd.arima.ndiffs(
                smartmeter_data.array, test="adf"
            )

            print(f"computed {first_differencing_order=}")

            if len(smartmeter_data) > 24:
                seasonal_differencing_term = pmd.arima.nsdiffs(
                    smartmeter_data.array, m=24, test="ocsb"
                )
                logging.info(f"computed {seasonal_differencing_term=}")
            else:
                logging.warning(
                    "unable to calculate seasonal_differencing_term due to small data set"
                )
                seasonal_differencing_term = 0

            start_time = time()
            model: pmd.ARIMA = pmd.auto_arima(
                y=smartmeter_data,
                X=weather_data,
                m=24,
                d=first_differencing_order,
                D=seasonal_differencing_term,
                trace=True,
                error_action="ignore",
                stepwise=True,
            )
            end_time = time()
            print("finished arima model training")

            if not isinstance(model, pmd.ARIMA):
                raise ValueError("pmdarima returned non-ARIMA model")

            metadata.training_time = Duration(seconds=(end_time - start_time))

        query = insert(Models).values(
            id=metadata.id,
            hash=metadata.generate_identifier(),
            meter=metadata.for_meter,
            comment=metadata.comment,
            training_start=datetime.fromtimestamp(start_time),
            training_duration=metadata.training_time,
            base_data_start=metadata.start_point,
            base_data_end=metadata.end_point,
            weather_capability=metadata.weather_capability,
            capability_column=metadata.capability_column,
            pickled_model=model,
        )

        print("storing model in database")
        with create_connection() as conn:
            conn.execute(query)
            conn.commit()

        print("model training finished")
