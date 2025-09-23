from flask import Flask, request, jsonify, json
from flask_cors import CORS
from controller import service_controller, model_handling
from controller.required_json_fields import require_json_fields_not_null
from interfaces import ServiceError
from werkzeug.sansio.response import Response
from werkzeug.exceptions import HTTPException, BadRequest
import logging, sys
import platform
from time import strftime, gmtime
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

prefix = "/waterdemand"

# logger setup
logging.basicConfig(
    # Capture all log levels from DEBUG and higher
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
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
@require_json_fields_not_null(
    "name",
    "timeframe",
    "resolution",
    "startpoint",
)
def single_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: amount of smartmeter data
    """

    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest

    data = service_controller.get_smartmeter_data(
        data["name"],
        data["timeframe"],
        data["resolution"],
        data["startpoint"],
    )
    return jsonify(data)


@app.route(f"{prefix}/trainModel", methods=["POST"])
@require_json_fields_not_null(
    "name",
    "timeframe",
    "resolution",
    "startpoint",
    "weatherCapability",
    "weatherColumn",
)
def train_model_on_smartmeter():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: predicted values with conf_intervals
    """

    data = request.json
    if data is None:
        raise BadRequest

    response = service_controller.train_model(
        data["name"],
        data["timeframe"],
        data["resolution"],
        data["startpoint"],
        data["weatherCapability"],
        data["weatherColumn"],
    )

    return jsonify(response)


@app.route(f"{prefix}/loadModelAndPredict", methods=["POST"])
@require_json_fields_not_null(
    "name",
    "timeframe",
    "resolution",
    "startpoint",
    "weatherCapability",
    "weatherColumn",
)
def pred_from_model():
    """
    get data of a chosen smartmeter and chosen timely frame
    :return: predicted values with conf_intervals
    """

    data = service_controller.forecast(
        request.json["name"],
        request.json["timeframe"],
        request.json["resolution"],
        request.json["startpoint"],
        request.json["weatherCapability"],
        request.json["weatherColumn"],
    )
    return jsonify(data)


@app.errorhandler(ServiceError)
def handle_errors(e: ServiceError) -> Response:
    return e.get_response()


@app.errorhandler(HTTPException)
def handle_http_exceptions(e: HTTPException) -> Response:
    response = e.get_response()
    response.data = json.dumps(
        {
            "type": "https://werkzeug.palletsprojects.com/en/stable/exceptions/#werkzeug.exceptions.HTTPException",
            "status": response.status_code,
            "title": response.status,
            "detail": e.description,
            "instance": f"tag:{platform.node()},{strftime("%Y-%m-%d", gmtime())}:{e.name}:{datetime.now().timestamp()}",
            "errors": [e.description],
            "host": platform.node(),
        }
    )

    response.content_type = "application/problem+json"
    return response

@app.errorhandler(Exception)
def handle_exceptions(e: Exception) -> Response:
    logging.error("Interal Server Error", exc_info=e)
    serviceError = ServiceError(
        "",
        500,
        "Internal Server Error",
        "The Service encountered a unexpected error during the handling of the request",
        [e]
    )
    return serviceError.get_response()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090, debug=False, use_reloader=False)
