from files import json_reader
import pandas as pd
import numpy as np
import pmdarima as pm
import matplotlib.pyplot as plt

def request_forecast(meter_name, timeframe: str, resolution: str):
    """
    main function to use when requesting a forecast by given data
    :param meter_name: name of the selected meter
    :param timeframe: number of rows
    :param resolution: density of data points
    :return: json_data to send to flask
    """
    df = create_ki_df(meter_name, timeframe, resolution)
    model = train_model(df)
    pred_df = create_forecast_data(model, df)

    json_data = pred_df.to_dict(orient="list")

    json_data["name"] = f"{meter_name}"
    json_data["timeframe"] = f"{timeframe}"
    json_data["resolution"] = f"{resolution}"

    return json_data

def create_ki_df(meter_name, timeframe: str, resolution: str):
    """
    create a df to alter for use in train model function
    :param meter_name: name of the selected smart meter
    :param timeframe: reference to how many data rows are used
    :param resolution: reference of the resolution of the data points
    :return: the specified dataframe
    """
    df = json_reader.create_df_from_smartmeter(meter_name, timeframe, resolution)

    df = df.set_index("dateObserved")
    df.index = pd.to_datetime(df.index, format="%d.%m.%y %H:%M")
    df["water_value_difference"] = df["numValue"].diff(periods=24)
    df["water_value_difference"] = df["water_value_difference"].bfill()
    df['hour_index'] = df.index.hour
    df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)

    return df

def train_model(df: pd.DataFrame):
    """
    create a trained SARIMAX Model based on the dataframe provided
    :param df: df provided based on selected smartmeter data
    :return: trained SARIMAX model
    """
    sarimax_model_without_exo = pm.auto_arima(df[['numValue']],
                                      start_p=1, start_q=1,
                                      test='adf',
                                      max_p=3, max_q=3, m=24, # 24 hour service
                                      start_P=0, seasonal=True,
                                      d=None, D=1,
                                      trace=False,
                                      error_action='ignore',
                                      suppress_warnings=True,
                                      stepwise=True)

    return sarimax_model_without_exo

def create_forecast_data(sarimax_model_without_exo, df: pd.DataFrame):
    """
    using the sarimax model forecast data is being predicted
    :param sarimax_model_without_exo: the model to use
    :param df: dataframe of the original data
    :return: df of confidence intervalls lower and upper and pred_values
    """
    sarimax_model = sarimax_model_without_exo

    # create forecast based on tutorial
    n_periods = 24

    # Generate future hourly timestamps
    future_index = pd.date_range(
        start=df.index[-1] + pd.Timedelta(hours=1),  # Start from the next hour
        periods=n_periods,
        freq='h'
    )

    # Compute cyclic encodings for the hours
    future_hour_sin = df['hour_sin']
    future_hour_cos = df['hour_cos']

    # Create a DataFrame for the exogenous variables
    future_exog = pd.DataFrame({
        'hour_sin': future_hour_sin,
        'hour_cos': future_hour_cos
    }, index=future_index)

    # Make predictions with confidence intervals
    fitted, confint = sarimax_model.predict(
        n_periods=n_periods,
        return_conf_int=True,
        exogenous=future_exog
    )

    # Create series for plotting and returning results
    fitted_series = pd.Series(fitted, index=future_index)
    lower_series = pd.Series(confint[:, 0], index=future_index)
    upper_series = pd.Series(confint[:, 1], index=future_index)

    # create dataframe from separate series
    final_df = pd.DataFrame({"lower_conf_values": lower_series, "numValue": fitted_series, "upper_conf_values":upper_series})
    final_df = final_df.reset_index()
    final_df = final_df.rename(columns={"index":"dateObserved"})
    final_df["dateObserved"] = final_df["dateObserved"].dt.strftime("%d.%m.%y %H:%M")

    #plot_forecast(df, fitted_series, lower_series, upper_series)

    return final_df

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



