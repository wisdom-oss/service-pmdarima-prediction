from flask import Flask, request, jsonify
from flask_cors import CORS
from controller import service_controller
import logging, sys

app = Flask(__name__)
CORS(app)

prefix = "/waterdemand"

# logger setup
logging.basicConfig(
    # Capture all log levels from DEBUG and higher
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

@app.route(f"{prefix}/helloworld", methods=["GET"])
def hello_world():
    return jsonify("Hello, World!")

@app.route(f"{prefix}/meterNames", methods=["GET"])
def request_meter_names():
    return jsonify(service_controller.get_meter_names())

@app.route(f"{prefix}/weatherCapabilities", methods=["GET"])
def request_weather_capabilities():
    resp = jsonify(service_controller.get_weather_capabilities(True))
    return resp

@app.route(f"{prefix}/weatherColumns", methods=["POST"])
def request_weather_column():

    req = request.json["capability"]
    data = service_controller.get_columns_of_capability(req)
    resp = jsonify(data)
    return resp


@app.route(f"{prefix}/singleSmartmeter", methods=["POST"])
def single_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: amount of smartmeter data
    """
    data = service_controller.get_smartmeter_data(request.json["name"],
                                                  request.json["timeframe"],
                                                  request.json["resolution"],
                                                  request.json["startpoint"]
                                                  )
    return jsonify(data)


@app.route(f"{prefix}/trainModel", methods=["POST"])
def train_model_on_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: predicted values with conf_intervals
    """

    service_controller.train_model(request.json["name"],
                                   request.json["timeframe"],
                                   request.json["resolution"],
                                   request.json["startpoint"],
                                   request.json["weatherCapability"],
                                   request.json["weatherColumn"]
                                   )

    return jsonify("Model saved")


@app.route(f"{prefix}/loadModelAndPredict", methods=["POST"])
def pred_from_model():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: predicted values with conf_intervals
    """

    data = service_controller.forecast(request.json["name"],
                                       request.json["timeframe"],
                                       request.json["resolution"],
                                       request.json["startpoint"],
                                       request.json["weatherCapability"],
                                       request.json["weatherColumn"]
                                       )
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8090, debug=False, use_reloader=False)