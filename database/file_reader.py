import os
import pandas as pd
from root_file import ROOT_DIR
from dotenv import load_dotenv


def format_smartmeter_data():
    df = read_smartmeter_data(False)

    # filter out unnecessary columns
    df = df[["dateObserved", "refDevice", "numValue"]]

    # shorten name handle
    device_prefix = os.getenv("DEVICE_PREFIX")
    df["refDevice"] = df["refDevice"].apply(lambda x: x.replace(device_prefix, ""))

    # add timezone information (none, because of utc)
    df["dateObserved"] = pd.to_datetime(df["dateObserved"], utc=True)

    return df

def read_smartmeter_data(metaCheck: bool):
    """
    read in the json data
    :param metaCheck: if true, read in meta data
    :return: df containing data
    """

    load_dotenv()

    abs_path = os.path.join(ROOT_DIR,
                            os.getenv("FILE_PATH_EXAMPLE_DATA"))
    if metaCheck:
        path = os.path.join(abs_path, os.getenv("EXAMPLE_META_DATA"))
    else:
        path = os.path.join(abs_path, os.getenv("EXAMPLE_DATA"))

    df = pd.read_json(path)

    return df



