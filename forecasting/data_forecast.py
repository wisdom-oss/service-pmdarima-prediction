import pandas as pd
import logging
from warnings import simplefilter
from pmdarima import ARIMA

def create_forecast_data(model: ARIMA, n_periods: int, exogenous_df: pd.DataFrame | None) -> pd.DataFrame:
    """
    using the sarimax model forecast data is being predicted
    
    :param model: the model to use
    :param exogenous_df: df containing all exogene variables to add to the prediction
    :param n_periods: number of periods (in hours) to predict into the future
    :return: df of confidence intervals
    lower and upper and pred_values
    """

    logging.debug("Creating forecast data")

    # ignore all future warnings
    simplefilter(action='ignore', category=FutureWarning)

    # Make predictions with confidence intervals
    predicted_values, conf_intervals = model.predict(
        n_periods=n_periods,
        X=exogenous_df,  # add exogenous variables when ready
        return_conf_int=True, # return confidence intervals
        alpha=0.1 # confidence interval of standard 95%
    )

    # create dataframe from separate series
    df = pd.DataFrame({"lower_conf_values": conf_intervals[:, 0],
                             "value": predicted_values,
                             "upper_conf_values": conf_intervals[:, 1]})

    logging.debug("Finished forecasting data")

    return df


def create_forecast_labels(last_timestamp: str, n_periods: int, resolution: str) -> pd.DatetimeIndex | None:
    """
    create the label timestamps for the forecasted data
    
    :param last_timestamp: last timestamp of the original data
    :param n_periods: number of periods (in hours) to predict into the future
    :param resolution: matched resolution
    :return: future labels
    """

    if resolution == "hourly":
        time_unit, frequency = "hours", "h"
    elif resolution == "daily":
        time_unit, frequency = "days", "D"
    elif resolution == "weekly":
        time_unit, frequency = "weeks", "W"
    else:
        raise ValueError("Unsupported resolution")

    # Generate future hourly timestamps
    last_ts = pd.to_datetime(last_timestamp)
    future_labels = pd.date_range(
        start=last_ts + pd.Timedelta(**{time_unit: 1}),  # Start from the next hour
        periods=n_periods,
        freq=frequency
    )

    return future_labels