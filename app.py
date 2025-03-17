from flask import Flask, request, jsonify
from flask_cors import CORS
from operations import requests as req
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

prefix = "/waterdemand"

@app.route(f"{prefix}/helloworld", methods=["GET"])
def hello_world():
    return "<p>Hello, World!</p>"


@app.route(f"{prefix}/meterInformation", methods=["GET"])
def meterInformation():
    try:
        return jsonify(req.read_meter_information())

    except Exception as e:
        print(e)
        # status code decided how angular understands response
        return jsonify({"error": str(e)}), 400


@app.route(f"{prefix}/singleSmartmeter", methods=["POST"])
def single_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: amount of smartmeter data
    """

    logging.debug("This is an Info")

    try:
        data = req.extract_single_smartmeter(request.json["name"],
                                             request.json["timeframe"],
                                             request.json["resolution"],
                                             request.json["startpoint"]
                                             )
        return jsonify(data)
    except Exception as e:
        print(f"error: {e}")
        return jsonify({"error": str(e)}), 400


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
        print(f"error: {e}")
        return jsonify({"error": str(e)}), 400


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
        print(f"error: {e}")
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=False)
