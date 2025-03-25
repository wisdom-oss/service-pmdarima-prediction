import pandas as pd
import numpy as np
import pmdarima as pm
import time
import logging

from pandas import DataFrame

from operations.calculations import weather

def time_it(func):
    """
    decorator function (@time_it) to measure execution time
    :param func: function to be provided (not necessary)
    :return: print the execution time
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        logging.debug(f"Execution time: {time.strftime('%H:%M:%S', time.gmtime(time.time() - start))}")
        return result
    return wrapper


def train_final_models(df: pd.DataFrame, capability: str):
    """
    create a trained SARIMAX Model based on the dataframe provided
    :param df: df provided based on selected smartmeter data
    :return: trained SARIMAX model
    """

    df["dateObserved"] = df["dateObserved"].dt.strftime('%d.%m.%y %H:%M')

    try:
        # m = number of observations per seasonal cycle (24 as in 24 observations in 1 day(season).
        # But 12 yields better results?

        exogen_df = None

        if capability != "plain":
            df_temperature = weather.request_weather_info(df["dateObserved"].tolist(), capability)
            logging.debug(f"Length Weather: {len(df_temperature)}, Length Training: {len(df)}")
            if not len(df) == len(df_temperature):
                raise ValueError(f"Necessary dataframes are not equal: {len(df)} != {len(df_temperature)}")
            exogen_df = df_temperature

        d_value = pm.arima.ndiffs(df["numValue"], test="adf")
        D_value = pm.arima.nsdiffs(df['numValue'], m=24, test='ocsb')
        logging.debug(f"Optimal d: {d_value} and D: {D_value}, Start Training \n")

        start_time = time.time()
        logging.debug(f"Start training at: {start_time}")

        model = pm.auto_arima(df['numValue'], X=exogen_df,
                              m=24,
                              seasonal=True,
                              d=d_value, D=D_value,
                              trace=1,
                              error_action='ignore',
                              suppress_warnings=True,
                              stepwise=True)

        end_time = time.time()
        logging.debug(f"End training at: {end_time}")

        training_time = end_time - start_time
        logging.debug(f"Duration of training: {training_time}")


        # original values: start_p=1, start_q=1,
        #                  max_p=3, max_q=3, m=24,
        #                  start_P=0, seasonal=True,
        #                  d=d_value, D=D_value,
        #                  trace=1, error_action='ignore',
        #                  suppress_warnings=True,
        #                  stepwise=True)

        logging.debug(model.summary())

        return model, training_time
    except ValueError as e:
        logging.debug(f"training failed, because of different weather lenghts" + e)
    except Exception as e:
        error_type = type(e).__name__
        logging.debug(f"Training Arima Model failed. \n {error_type}: {e}")


def create_labels(df: pd.DataFrame, resolution: str = "hourly") -> DataFrame | None:
    n_periods = 24

    try:
        match resolution:
            case "hourly":
                time_unit, frequency = "hours", "h"
            case "daily":
                time_unit, frequency = "days", "D"
            case "weekly":
                time_unit, frequency = "weeks", "W"
            case _:
                time_unit, frequency = None


        df.dateObserved = pd.to_datetime(df.dateObserved)
        # Generate future hourly timestamps
        future_index = pd.date_range(
            start=df.dateObserved.iloc[-1] + pd.Timedelta(**{time_unit: 1}),  # Start from the next hour
            periods=n_periods,
            freq=frequency
        )

        df = pd.DataFrame(future_index, columns=['Date'])
        return df
    except Exception as e:
        error_type = type(e).__name__
        logging.debug(f"Creating Labels for predicted values failed. \n {error_type}: {e}")


def create_forecast_data(model, n_periods: int, exogenous_df: pd.DataFrame):
    """
    using the sarimax model forecast data is being predicted
    :param exogenous_df: df containing all exogene variables to add to the prediction
    :param n_periods: number of periods (in hours) to predict into the future
    :param model: the model to use
    :return: df of confidence intervalls
    lower and upper and pred_values
    """

    try:

        # Make predictions with confidence intervals
        predicted_values, conf_intervals = model.predict(
            n_periods=n_periods,
            X=exogenous_df,  # add exogenous variables when ready
            return_conf_int=True, # return confidence intervalls
            alpha=0.1 # confidence intervall of standard 95%
        )
    except Exception as e:
        error_type = type(e).__name__
        logging.debug(f"Predicting values failed. \n {error_type}: {e}")

    # create dataframe from separate series
    final_df = pd.DataFrame({"lower_conf_values": conf_intervals[:, 0], "numValue": predicted_values,
                             "upper_conf_values": conf_intervals[:, 1]})

    return final_df


def create_exogenous_variables(prediction_indexes):
    df = pd.DataFrame()

    # create an index for the hours of a day NOTE: Change for different resolutions!
    df['hour_index'] = df.index.hour
    df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)

    # Create a DataFrame for the exogenous variables and plug them in
    future_exog = pd.DataFrame({
        'hour_sin': df['hour_sin'],
        'hour_cos': df['hour_cos']
    }, index=prediction_indexes)

    return future_exog





