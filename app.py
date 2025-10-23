from flask import Flask
from flask_json import FlaskJSON
from os import makedirs
from settings import Settings

config = Settings()

app = Flask(__name__)

import routes.hello_world
import routes.meter_names
import routes.weather_capabilities
import routes.weather_columns
import routes.single_smartmeter
import routes.train_model
import routes.forecast_with_model


if __name__ == "__main__":

    makedirs(config.result_storage_location, exist_ok=True)
    makedirs(config.example_data_storage_location, exist_ok=True)
    makedirs(config.trained_model_storage_location, exist_ok=True)


    app.config["JSON_USE_ENCODE_METHODS"] = True
    app.run(host="0.0.0.0", load_dotenv=True)
