import pandas as pd
import numpy as np
import pmdarima as pm
import matplotlib.pyplot as plt
import time
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
        print(f"Execution time: {time.strftime('%H:%M:%S', time.gmtime(time.time() - start))}")
        return result
    return wrapper

def train_model(exogenous: bool, df: pd.DataFrame):
    """
    train a model based on a flag with or without exogenous variables
    :param exogenous: true if exogenous variables are used
    :param df: dataframe
    :return: trained model
    """

    if exogenous:
        return train_exogenous_model(df)
    elif not exogenous:
        return train_plain_model(df)

@time_it
def train_plain_model(df: pd.DataFrame):
    """
    create a trained SARIMAX Model based on the dataframe provided
    :param df: df provided based on selected smartmeter data
    :return: trained SARIMAX model
    """

    try:
        # m = number of observations per seasonal cycle (24 as in 24 observations in 1 day(season).
        # But 12 yields better results?
        model = pm.auto_arima(df['numValue'],
                              start_p=1, start_q=1,
                              test='adf',
                              max_p=3, max_q=3, m=24,
                              start_P=0, seasonal=True,
                              d=0, D=1, # d =None so No Integrating was done
                              trace=1,
                              error_action='ignore', #default: ignore
                              suppress_warnings=True,
                              stepwise=True)

        print(model.summary())

        return model
    except Exception as e:
        print(e)
        raise ValueError(e)


@time_it
def train_exogenous_model(df: pd.DataFrame):
    """
    create a trained SARIMAX Model based on the dataframe provided
    :param df: df provided based on selected smartmeter data
    :return: trained SARIMAX model
    """

    df["dateObserved"] = df["dateObserved"].dt.strftime('%d.%m.%y %H:%M')

    df_temperature = weather.request_weather_info(df["dateObserved"].tolist())

    try:
        # m = number of observations per seasonal cycle (24 as in 24 observations in 1 day(season).
        # But 12 yields better results?
        model = pm.auto_arima(df['numValue'], df_temperature,
                              start_p=1, start_q=1,
                              test='adf',
                              max_p=3, max_q=3, m=24,
                              start_P=0, seasonal=True,
                              d=0, D=1, # d =None so No Integrating was done
                              trace=1,
                              error_action='ignore', #default: ignore
                              suppress_warnings=True,
                              stepwise=True)

        print(model.summary())

        return model
    except Exception as e:
        print(e)
        raise ValueError(e)


def create_labels(df: pd.DataFrame, resolution: str = "hourly"):
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

        return future_index

    except Exception as e:
        print(e)
        return None


def create_forecast_data(model, n_periods: int, exogenous_df: pd.DataFrame):
    """
    using the sarimax model forecast data is being predicted
    :param exogenous_df: df containing all exogene variables to add to the prediction
    :param n_periods: number of periods (in hours) to predict into the future
    :param model: the model to use
    :return: df of confidence intervalls
    lower and upper and pred_values
    """
    sarimax_model = model

    # Generate a dataframe of all exogenous variable to use while predicting data
    #future_exog = create_exogenous_variables_for_prediction(future_index)

    try:

        # Make predictions with confidence intervals
        predicted_values, conf_intervals = sarimax_model.predict(
            n_periods=n_periods,
            X=exogenous_df,  # add exogenous variables when ready
            return_conf_int=True, # return confidence intervalls
            alpha=0.01 # confidence intervall of 95%
        )
    except Exception as e:
        print(f" prediction {e}")

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


def plot_forecast(df, fitted_series, lower_series, upper_series):
    # Plot
    plt.figure(figsize=(15, 7))
    plt.plot(df["numValue"], color='#1f76b4')
    plt.plot(fitted_series, color='darkgreen')
    plt.fill_between(lower_series.index,
                     lower_series,
                     upper_series,
                     color='k', alpha=.15)

    plt.title("SARIMAX - Forecast of Smartmeter Data")
    plt.show()





