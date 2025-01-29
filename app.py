import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from files import json_reader as st
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

    data = st.read_meter_information()

    return data

@app.route(prefix + "/singleSmartmeter", methods = ["POST"])
def single_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: amount of smartmeter data
    """
    response = request.json
    data = st.extract_single_smartmeter(response["name"],
                                        response["timeframe"],
                                        response["resolution"]
                                        )
    return jsonify(data)

@app.route(prefix + "/predSingleSmartmeter", methods = ["POST"])
def pred_single_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: predicted values with conf_intervals
    """
    response = request.json
    data = pred.request_forecast(response["name"],
                                        response["timeframe"],
                                        response["resolution"]
                                        )
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=False)

