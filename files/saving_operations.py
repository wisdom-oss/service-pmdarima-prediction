from dotenv import load_dotenv
import joblib
import os
import re

def save_model_by_name(model, name:  str, timeframe: str, resolution: str):
    """
    method to save a created model to a pickle file, based on the parameters provided
    :param model: trained model object
    :param name: name of the smartmeter
    :param timeframe: amount of days
    :param resolution: timely resolution
    :return: print
    """
    path = __create_path_to_file(name, timeframe, resolution)

    try:
        # Pickle it
        joblib.dump(model, path, compress=3)
    except Exception as e:
        print(e)
    finally:
       print("Model successfully saved")

def load_model_by_name(name:  str, timeframe: str, resolution: str):
    """
    method to save a created model to a pickle file, based on the parameters provided
    :param name: name of the smartmeter
    :param timeframe: amount of days
    :param resolution: timely resolution
    :return: loaded model
    """
    path = __create_path_to_file(name, timeframe, resolution)

    try:
        # Load the model up, create predictions
        return joblib.load(path)
    except Exception as e:
        print(f"Loading Model failed, because of: {e}")

def __create_path_to_file(name:  str, timeframe: str, resolution: str):
    """
    helper function to create a unique name and keep it consistent throughout the project
    :param name: smartmeter name
    :param timeframe: duration of days
    :param resolution: timely resolution
    :return: full name + path to folder
    """
    load_dotenv()
    root = f"{os.getenv("ROOT_DIR")}"
    folder_path = f"{os.getenv("FILE_PATH_TRAINED_MODELS")}"

    identifier = f"{resolution}-{timeframe}-{name}-model.pkl"

    identifier = identifier.replace(":","-")
    identifier = identifier.replace(" ","-")

    full_path = os.path.join(root, folder_path, identifier)

    return full_path

def has_duplicates(name:  str, timeframe: str, resolution: str):
    """
    create a temp name and check if model already exists
    :param name: smartmeter
    :param timeframe: duration of days
    :param resolution: timely resolution
    :return: True if duplicate, False else
    """
    path = __create_path_to_file(name, timeframe, resolution)

    if os.path.exists(path):
        return True;
    else:
        return False