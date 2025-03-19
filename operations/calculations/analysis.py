import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging
import pandas as pd

def analyze_prediction(real_values, forecast_values):
    mae = mean_absolute_error(real_values, forecast_values)
    mse = mean_squared_error(real_values, forecast_values)
    r2 = r2_score(real_values, forecast_values)
    rmse = np.sqrt(mse)

    logging.debug(f"\n"
                  f"Mean absolute error: {mae} \n"
                  f"Mean squared error: {mse} \n"
                  f"R2 score: {r2} \n"
                  f"RMSE: {rmse} \n")

    df = pd.DataFrame(data=[mae,mse,rmse,r2], columns=["MAE", "MSE", "RMSE", "R2"])

    return df