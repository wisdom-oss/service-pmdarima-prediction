from dotenv import load_dotenv
import joblib
import os

def save_model_by_name(model, name:  str, timeframe: str, resolution: str):
    """
    saves a trained arima model to a pickle file
    :param model: trained model
    :param name: name of smartmeter
    :param timeframe: amount of days
    :param resolution: resolution of labels
    :return: success or error message
    """
    path = __create_path_to_file(name, timeframe, resolution)

    try:
        # Pickle it
        joblib.dump(model, path, compress=3)
        data = f"Model successfully saved to {path}"
    except Exception as e:
        data = f"An error occurred while saving to {path}: {e}"
    finally:
        print(data)
        return data

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
        data = joblib.load(path)
    except Exception as e:
        data = f"Loading Model in {path} failed, because of: {e}"
        print(data)
    finally:
        return data

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

    identifier = identifier.replace(":","_")

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
    full_path = __create_path_to_file(name, timeframe, resolution)

    if os.path.exists(full_path):
        return True
    else:
        return False