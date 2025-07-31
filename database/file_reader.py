import os
import pandas as pd
from root_file import ROOT_DIR
from dotenv import load_dotenv


def format_smartmeter_data() -> pd.DataFrame:
    df = __read_smartmeter_data(False)

    # filter out unnecessary columns
    df = df[["dateObserved", "refDevice", "numValue"]]

    # shorten name handle
    device_prefix = os.getenv("DEVICE_PREFIX")
    df["refDevice"] = df["refDevice"].apply(lambda x: x.replace(device_prefix, ""))

    # add timezone information (none, because of utc)
    df["dateObserved"] = pd.to_datetime(df["dateObserved"], utc=True)

    return df

def __read_smartmeter_data(meta_check: bool) -> pd.DataFrame:
    """
    read in the json data
    
    :param metaCheck: if true, read in metadata
    :return: df containing data
    """

    load_dotenv()
    file_path_ex_data = os.getenv("FILE_PATH_EXAMPLE_DATA")

    abs_path = os.path.join(ROOT_DIR, file_path_ex_data)
    if meta_check:
        example_meta = os.getenv("EXAMPLE_META_DATA")
        path = os.path.join(abs_path,example_meta)
    else:
        example_data = os.getenv("EXAMPLE_DATA")
        path = os.path.join(abs_path, example_data)

    df = pd.read_json(path)

    return df



