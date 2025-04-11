import logging
import time
import pmdarima as pm
import pandas as pd

def train_model(df: pd.DataFrame, weather_df: pd.DataFrame or None):
    """
    train a model based on the data and exogen weather data
    :param df: smartmeter data
    :param weather_df: weather information
    :return: trained model and set training time
    """

    d_value = pm.arima.ndiffs(df["value"], test="adf")
    D_value = pm.arima.nsdiffs(df['value'], m=24, test='ocsb')
    logging.debug(f"Optimal d: {d_value} and D: {D_value}, Start Training \n")

    start_time = time.time()
    logging.debug(f"Start training at: {start_time}")

    model = pm.auto_arima(df['value'], X=weather_df,
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
    logging.debug(model.summary())

    return model, training_time