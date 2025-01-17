import os

from flask import Flask, request
from flask_cors import CORS
from files import json_reader as st
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
    return st.read_meter_information()

@app.route(prefix + "/singleSmartmeter", methods = ["POST"])
def requestSingleSmartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: amount of smartmeter data
    """
    response = request.json
    data = st.extract_single_smartmeter(response["name"], response["timeframe"])
    return data

if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=False)

