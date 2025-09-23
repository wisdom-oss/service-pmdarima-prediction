import logging
import joblib
import os
import interfaces
from dotenv import load_dotenv
from root_file import ROOT_DIR


def save_model_by_name(model: interfaces.ModelInfoDict, name: str, timeframe: str, resolution: str, start_point: str, capability: str, column_name: str) -> None:
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

    if path is None:
        raise TypeError("Path cannot be None")

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        # Pickle it
        joblib.dump(model, path, compress=3)
        logging.debug(f"Model saved to {path}")
    except Exception as e:
        logging.debug(f"Error during saving of {path}: {e}")
        raise e


def load_model_by_name(name: str, timeframe: str, resolution: str, start_point: str, capability: str, column_name: str) -> interfaces.ModelInfoDict | None:
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
        data = joblib.load(path)
    except FileNotFoundError:
        raise interfaces.ServiceError("", 424, "Model Not Trained", "The model you tried to use for a prediction has not been trained yet")
    return data


def model_is_unique(name: str, timeframe: str, resolution: str, start_point: str, capability: str,
                    column_name: str) -> bool:
    """
    check for duplicate models to reduce server usage and prevent multiple model training
    :param name:
    :param timeframe:
    :param resolution:
    :param start_point:
    :param capability:
    :param column_name:
    :return:
    """
    path = __create_file_path(name, timeframe, resolution, start_point, capability, column_name)

    """
    return true if model is unique, else false
    """
    if __has_duplicates(path):
        return False
    else:
        return True


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

    return full_path


def __has_duplicates(full_path: str) -> bool:
    """
    create a temp name and check if model already exists
    
    :param full_path: name of file to test
    :return: True if duplicate, False else
    """

    load_dotenv()
    allow = os.getenv("ALLOW_DUPLICATE_MODELS", "false").strip().lower() == "true"

    # only perform duplicate check if env variable is False
    if not allow:
        if os.path.exists(full_path):
            logging.debug(f"{full_path} already exists. Cancel training")
            return True
        else:
            logging.debug(f"{full_path} unique. Continue training")
            return False
    else:
        logging.debug("ALLOW DUPLICATE FLAG ignored")
        return False
