def transform_single_meter_request(df, meter_name, timeframe, startingTime):

    test = df[df.refDevice != meter_name].index
    # Doesnt work anymore -> index does not match

    # filter every meter not being named
    df = df.drop(df[df.refDevice != meter_name].index)

    # filter for date and values
    df = df[["dateObserved", "numValue"]]

    json_data = df.to_dict(orient="list")

    json_data["name"] = meter_name
