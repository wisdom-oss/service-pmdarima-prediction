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

@app.route(prefix + "/waterdemand/meterInformation", methods = ["GET"])
def meterInformation():
    return f"test"

@app.route(prefix + "/realData", methods = ["GET"])
def getRealData():
    data = st.transform_data("single", 100)
    return data

if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=False)

