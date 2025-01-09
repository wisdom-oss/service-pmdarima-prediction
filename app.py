import os

from flask import Flask
from flask_cors import CORS
from smartmeterdata import smartmeter_transformer as st
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
    return st.get_meter_information()


@app.route(prefix + "/singleRealData", methods = ["GET"])
def getRealData():
    data = st.extract_single_smartmeter("single", 100)
    return data

#@app.route(prefix + "/postRequest", methods = ["POST"])
def getRealData():
    # request library? Handle Post Requests
    data = st.extract_single_smartmeter("single", 100)
    return data

if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=False)

