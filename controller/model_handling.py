import logging
from typing import Any
import joblib
import os
from dotenv import load_dotenv
from root_file import ROOT_DIR


def save_model_by_name(model: dict, name: str, timeframe: str, resolution: str, start_point: str, capability: str, column_name: str) -> None:
    """
    :param model: model to save
    :param name: name of model
    :param timeframe: duration of time series data trained
    :param resolution: resolution of time series data trained
    :param start_point: start of time series
    :param capability: weather capability to train
    :param column_name: column name of the weather capability
    :return: None
    """

    path = __create_file_path(name, timeframe, resolution, start_point, capability, column_name)

    try:
        # Pickle it
        joblib.dump(model, path, compress=3)
        logging.debug(f"Model saved to {path}")
    except Exception as e:
        logging.debug(f"Error during saving of {path}: {e}")


def load_model_by_name(name: str, timeframe: str, resolution: str, start_point: str, capability: str, column_name: str) -> dict[str, Any] | None:
    """
    method to load a model by name and parameters

    :param name: name of model
    :param timeframe: duration of time series data trained
    :param resolution: resolution of time series data trained
    :param start_point: start of time series
    :param capability: weather capability to train
    :param column_name: column name of the weather capability
    :return: None
    """


    path = __create_file_path(name, timeframe, resolution, start_point, capability, column_name)

    if path is None:
        logging.debug(f"Created Path is None")
        raise TypeError(f"Created Path is None")

    try:
        # Load the model up, create predictions
        data = joblib.load(path)
        return data
    except Exception as e:
        logging.debug(f"Loading {path} failed: {e}")
        return None


def __create_file_path(name: str, timeframe: str, resolution: str, start_point: str, capability: str, column_name: str) -> str | None:
    """
    create a unique file name which is used to save and retrieve trained model data by name

    :param name: smartmeter name
    :param timeframe: duration of timesries
    :param resolution: resolution of timesries
    :param start_point: first day of timeseries
    :param capability: kind of weather data | plain if none
    :param column_name: name of weather data related column | none if no weather data
    :return: unique file name
    """

    if capability == "plain":
        column_name = "no_column"

    file_name = f"{resolution}-{timeframe}-{name}-{start_point}-{capability}-{column_name}.pkl"
    file_name = file_name.replace(" ", "-")
    file_name = file_name.replace(":", "-")

    load_dotenv()
    folder_path = f"{os.getenv("FILE_PATH_TRAINED_MODELS")}"
    full_path = os.path.join(ROOT_DIR, folder_path, file_name)

    if not __has_duplicates(full_path):
        return full_path

    return None


def __has_duplicates(full_path: str) -> bool:
    """
    create a temp name and check if model already exists
    
    :param file_name: name of file to test
    :return: True if duplicate, False else
    """

    load_dotenv()
    allow = os.getenv("ALLOW_DUPLICATE_MODELS")

    # only perform duplicate check if env variable is False
    if not allow:
        if os.path.exists(full_path):
            logging.debug(f"{full_path} already exists. Cancel saving")
            return True
        else:
            logging.debug(f"{full_path} unique. Continue saving")
            return False
    else:
        logging.debug("ALLOW DUPLICATE FLAG ignored")
        return False
