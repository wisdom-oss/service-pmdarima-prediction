from files import saving_operations as so

from files import json_reader
import pandas as pd
import numpy as np
import pmdarima as pm
import matplotlib.pyplot as plt

def train_and_save_model(meter_name: str, timeframe: str, resolution: str):
    # create a dataframe based on the provided parameters
    df = json_reader.create_df_from_smartmeter(meter_name, timeframe, resolution)

    if not so.has_duplicates(meter_name, timeframe, resolution):
        # train the model if identifier is unique
        model = __train_model(df)
        so.save_model_by_name(model, meter_name, timeframe, resolution)
    else:
        raise ValueError("model exists already!")

def load_and_use_model(meter_name: str, timeframe: str, resolution: str):
    model = so.load_model_by_name(meter_name, timeframe, resolution)

    pred_df = __create_forecast_data(model, 24, None)

    # add bonus information back to dataframe
    json_data = pred_df.to_dict(orient="list")
    json_data["name"] = f"{meter_name}"
    json_data["timeframe"] = f"{timeframe}"
    json_data["resolution"] = f"{resolution}"

    return json_data

def request_forecast(meter_name, timeframe: str, resolution: str):
    """
    main function to use when requesting a forecast by given data
    :param meter_name: name of the selected meter
    :param timeframe: number of rows
    :param resolution: density of data points
    :return: json_data to send to flask
    """

    # create a dataframe based on the provided parameters
    df = json_reader.create_df_from_smartmeter(meter_name, timeframe, resolution)

    # train the model
    model = __train_model(df)

    # create prediction values (series, conf intervals) from trained model
    # hand in number of periods and df of exogenous variables to predict
    #pred_df = __create_forecast_data(model, 24)

    pred_df = __create_forecast_data(model, 24, None)

    # ADD date labels back HERE

    # add bonus information back to dataframe
    json_data = pred_df.to_dict(orient="list")
    json_data["name"] = f"{meter_name}"
    json_data["timeframe"] = f"{timeframe}"
    json_data["resolution"] = f"{resolution}"

    return json_data

def __train_model(df: pd.DataFrame):
    """
    create a trained SARIMAX Model based on the dataframe provided
    :param df: df provided based on selected smartmeter data
    :return: trained SARIMAX model
    """

    try:
        model = pm.auto_arima(df[['numValue']],
                                          start_p=1, start_q=1,
                                          test='adf',
                                          max_p=3, max_q=3, m=24, # 24 hour service
                                          start_P=0, seasonal=True,
                                          d=None, D=1,
                                          trace=1,
                                          error_action='ignore',
                                          suppress_warnings=False,
                                          stepwise=True)
        return model
    except Exception as e:
        print(e)
        return str(e)

def __create_forecast_data(model, n_periods: int, exogenous_df: pd.DataFrame=None):
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

    # Make predictions with confidence intervals
    predicted_values, conf_intervals = sarimax_model.predict(
        n_periods=n_periods,
        return_conf_int=True,
        exogenous=exogenous_df # add exogenous variables when ready
    )

    # create dataframe from separate series
    final_df = pd.DataFrame({"lower_conf_values": conf_intervals[:, 0], "numValue": predicted_values, "upper_conf_values":conf_intervals[:, 1]})
    final_df = final_df.reset_index()
    final_df = final_df.rename(columns={"index":"dateObserved"})

    return final_df

def __create_exogenous_variables(prediction_indexes):
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

def __plot_forecast(df, fitted_series, lower_series, upper_series):
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



