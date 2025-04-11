import pandas as pd
import logging

from warnings import simplefilter

def create_forecast_data(model, n_periods: int, exogenous_df: pd.DataFrame):
    """
    using the sarimax model forecast data is being predicted
    :param model: the model to use
    :param exogenous_df: df containing all exogene variables to add to the prediction
    :param n_periods: number of periods (in hours) to predict into the future
    :return: df of confidence intervalls
    lower and upper and pred_values
    """

    logging.debug("Creating forecast data")

    # ignore all future warnings
    simplefilter(action='ignore', category=FutureWarning)

    # Make predictions with confidence intervals
    predicted_values, conf_intervals = model.predict(
        n_periods=n_periods,
        X=exogenous_df,  # add exogenous variables when ready
        return_conf_int=True, # return confidence intervalls
        alpha=0.1 # confidence intervall of standard 95%
    )

    # create dataframe from separate series
    df = pd.DataFrame({"lower_conf_values": conf_intervals[:, 0],
                             "value": predicted_values,
                             "upper_conf_values": conf_intervals[:, 1]})

    logging.debug("Finished forecasting data")

    return df


def create_forecast_labels(last_timestamp, n_periods: int, resolution: str) -> list or None:

    match resolution:
        case "hourly":
            time_unit, frequency = "hours", "h"
        case "daily":
            time_unit, frequency = "days", "D"
        case "weekly":
            time_unit, frequency = "weeks", "W"
        case _:
            time_unit, frequency = None, None

    # Generate future hourly timestamps
    future_index = pd.date_range(
        start=last_timestamp + pd.Timedelta(**{time_unit: 1}),  # Start from the next hour
        periods=n_periods,
        freq=frequency
    )

    return future_index