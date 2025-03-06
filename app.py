import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from files import json_reader
from calculations import predictions as pred
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()
prefix = os.getenv("API_PREFIX")

@app.route(prefix + "/helloworld", methods = ["GET"])
def hello_world():
    return "<p>Hello, World!</p>"

@app.route(prefix + "/meterInformation", methods = ["GET"])
def meterInformation():

    try:
        return jsonify(json_reader.read_meter_information())

    except Exception as e:
        print(e)
        # status code decided how angular understands response
        return jsonify({"error": str(e)}), 400


@app.route(prefix + "/singleSmartmeter", methods = ["POST"])
def single_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: amount of smartmeter data
    """
    response = request.json

    try:
        data = json_reader.extract_single_smartmeter(response["name"],
                                            response["timeframe"],
                                            response["resolution"]
                                            )
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route(prefix + "/trainModel", methods = ["POST"])
def train_model_on_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: predicted values with conf_intervals
    """
    response = request.json
    identifier = response["name"] + "-" + response["timeframe"] + "-" + response["resolution"]

    print("Start training model!")

    try:
        pred.train_and_save_model(response["name"], response["timeframe"], response["resolution"])
        data = "Creating model successfully for: " + identifier
        print("Creating model successfully for: " + identifier)
        return jsonify(data)
    except Exception as e:
        print("Creating model failed for: " + identifier + ", because of \n" + str(e))
        return jsonify({"error": str(e)}), 400

@app.route(prefix + "/loadModelAndPredict", methods = ["POST"])
def pred_from_model():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: predicted values with conf_intervals
    """
    response = request.json

    print("Start creating forecast!")
    identifier = response["name"] + "-" + response["timeframe"] + "-" + response["resolution"]

    try:
        data = pred.load_and_use_model(response["name"],
                                            response["timeframe"],
                                            response["resolution"]
                                            )

        print("Creating forecast successfully for: " + identifier)
        return jsonify(data)
    except Exception as e:
        print(f"Creating forecast failed for: {identifier}, because of \n {str(e)}")
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=False)

