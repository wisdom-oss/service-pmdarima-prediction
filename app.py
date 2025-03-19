from flask import Flask, request, jsonify
from flask_cors import CORS
from operations import requests as req
import logging, sys

app = Flask(__name__)
CORS(app)

prefix = "/waterdemand"

# Set up logging to capture both console output (stdout) and log file
logging.basicConfig(
    level=logging.DEBUG,  # Capture all log levels from DEBUG and higher
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log output will appear in the console (stdout)
        # logging.FileHandler("arima_model.log", mode='a')  # Save logs to arima_model.log file
    ]
)

@app.route(f"{prefix}/helloworld", methods=["GET"])
def hello_world():
    return "<p>Hello, World!</p>"


@app.route(f"{prefix}/meterInformation", methods=["GET"])
def meterInformation():
    try:
        return jsonify(req.read_meter_information())

    except Exception as e:
        logging.debug(e)
        # status code decided how angular understands response
        return jsonify({"error in /meterInformation": str(e)}), 400


@app.route(f"{prefix}/singleSmartmeter", methods=["POST"])
def single_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: amount of smartmeter data
    """

    try:
        data = req.extract_single_smartmeter(request.json["name"],
                                             request.json["timeframe"],
                                             request.json["resolution"],
                                             request.json["startpoint"]
                                             )
        return jsonify(data)
    except Exception as e:
        logging.debug(f"error in /singleSmartmeter: {e}")
        return jsonify({"error in /singleSmartmeter": str(e)}), 400


@app.route(f"{prefix}/trainModel", methods=["POST"])
def train_model_on_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: predicted values with conf_intervals
    """
    print("Start training model!")

    try:
        data = req.train_and_save_model(request.json["name"],
                                        request.json["timeframe"],
                                        request.json["resolution"],
                                        request.json["startpoint"],
                                        request.json["useWeather"]
                                        )
        return jsonify(data)
    except Exception as e:
        logging.debug(f"error in /trainModel: {e}")
        return jsonify({"error in /trainModel": str(e)}), 400


@app.route(f"{prefix}/loadModelAndPredict", methods=["POST"])
def pred_from_model():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: predicted values with conf_intervals
    """
    print("Start creating forecast!")

    try:
        data = req.load_and_use_model(request.json["name"],
                                      request.json["timeframe"],
                                      request.json["resolution"],
                                      request.json["startpoint"],
                                      request.json["useWeather"]
                                      )

        return jsonify(data)
    except Exception as e:
        logging.debug(f"error in /loadModelAndPredict: {e}")
        return jsonify({"error in /loadModelAndPredict": str(e)}), 400


if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=False)
