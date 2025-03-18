from dotenv import load_dotenv
import joblib
import os
from root_file import ROOT_DIR
import logging

def save_model_by_name(model, name:  str, timeframe: str, resolution: str, startpoint: str, exogen: bool):
    """
    saves a trained arima model to a pickle file
    :param model: trained model
    :param name: name of smartmeter
    :param timeframe: amount of days
    :param resolution: resolution of labels
    :return: success or error message
    """
    path = __create_path_to_file(name, timeframe, resolution, startpoint, exogen)

    try:
        # Pickle it
        joblib.dump(model, path, compress=3)
        data = f"Model successfully saved to {path}"
    except Exception as e:
        data = f"An error occurred while saving to {path}: {e}"
    finally:
        logging.debug(data)
        return data

def load_model_by_name(name:  str, timeframe: str, resolution: str,startpoint: str, exogen: bool):
    """
    method to save a created model to a pickle file, based on the parameters provided
    :param name: name of the smartmeter
    :param timeframe: amount of days
    :param resolution: timely resolution
    :return: loaded model
    """
    path = __create_path_to_file(name, timeframe, resolution, startpoint, exogen)

    try:
        # Load the model up, create predictions
        data = joblib.load(path)
    except Exception as e:
        error_type = type(e).__name__
        data = f"Loading Model in {path} failed. \n {error_type}: {e}"
        logging.debug(data)
    finally:
        return data

def __create_path_to_file(name:  str, timeframe: str, resolution: str, startpoint: str, exogen: bool):
    """
    helper function to create a unique name and keep it consistent throughout the project
    :param name: smartmeter name
    :param timeframe: duration of days
    :param resolution: timely resolution
    :return: full name + path to folder
    """

    if exogen:
        identifier = f"{resolution}-{timeframe}-{name}-{startpoint}-exogen.pkl"
    else:
        identifier = f"{resolution}-{timeframe}-{name}-{startpoint}-plain.pkl"

    identifier = identifier.replace(":","_")

    load_dotenv()
    folder_path = f"{os.getenv("FILE_PATH_TRAINED_MODELS")}"
    full_path = os.path.join(ROOT_DIR, folder_path, identifier)

    return full_path

def has_duplicates(name:  str, timeframe: str, resolution: str, startpoint: str):
    """
    create a temp name and check if model already exists
    :param startpoint:
    :param name: smartmeter
    :param timeframe: duration of days
    :param resolution: timely resolution
    :return: True if duplicate, False else
    """

    load_dotenv()
    allow = os.getenv("ALLOW_DUPLICATE_MODELS")

    # only perform duplicate check if env variable is False
    if not allow:
        full_path = __create_path_to_file(name, timeframe, resolution, startpoint)
        if os.path.exists(full_path):
            return True
        else:
            return False
    else:
        return False