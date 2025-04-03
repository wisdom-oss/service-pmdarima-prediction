import os
import pandas as pd
from root_file import ROOT_DIR
from dotenv import load_dotenv
from datetime import datetime, timezone

def format_smartmeter_data():
    df = __read_smartmeter_data(False)

    # filter out unnecessary columns
    df = df[["dateObserved", "refDevice", "numValue"]]

    # shorten name handle
    device_prefix = os.getenv("DEVICE_PREFIX")
    df["refDevice"] = df["refDevice"].apply(lambda x: x.replace(device_prefix, ""))
    df["refDevice"] = df["refDevice"].apply(lambda x: x.replace("-household", ""))

    # format time to incorporate timezone
    origin_format = os.getenv("DATETIME_ORIGIN")
    utc_format = os.getenv("DATETIME_UTC_ENSURE")
    df['dateObserved'] = df['dateObserved'].apply(lambda x: datetime.strptime(x, origin_format)
                                                  .replace(tzinfo=timezone.utc)
                                                  .strftime(utc_format))

    return df

def __read_smartmeter_data(metaCheck: bool):
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

