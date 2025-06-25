import numpy as np
import logging
import pandas as pd

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def calculate_metrics(real_values: dict, forecast_values: dict) -> pd.DataFrame:
    # BUG? Comparing real_values of the train set with predicted values of the test set?
    """
    compare values to determine either the model itself (compare real values test set vs forecast values)
    or the predictive power real values in 24h period vs predicted values 24h period.
    :param real_values: values measured for smartmeter
    :param forecast_values: predicted values of pmdarima
    :return: df with values
    """
    mae = mean_absolute_error(real_values, forecast_values)
    mse = mean_squared_error(real_values, forecast_values)
    rmse = np.sqrt(mse)
    r2 = r2_score(real_values, forecast_values)

    logging.debug(f"\n"
                  f"Mean absolute error: {mae} \n"
                  f"Mean squared error: {mse} \n"
                  f"RMSE: {rmse} \n"
                  f"R2 score: {r2} \n")

    df = pd.DataFrame(data=[[mae, mse, rmse, r2]], columns=["MAE", "MSE", "RMSE", "R2"])

    return df

