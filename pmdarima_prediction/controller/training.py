from .. import config
import warnings
import pandas as pd
import pmdarima as pmd
import logging
from contextlib import redirect_stdout
from os import path

from time import time

from pydantic_extra_types.pendulum_dt import Duration

from ..classes import ModelMetaData
from ..controller import storage


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

            # TODO: implement redis client to signalize training of model to other instances

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
            storage.store_model(model, metadata)

            print("DONE TRAINING")
