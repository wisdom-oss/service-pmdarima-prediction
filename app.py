from flask import Flask
from flask_json import FlaskJSONProvider
from os import makedirs
from settings import Settings

config: Settings

app = Flask(__name__)
FlaskJSONProvider(app)

import routes.hello_world
import routes.meter_names

if __name__ == "__main__":

    config = Settings()

    makedirs(config.result_storage_location, exist_ok=True)
    makedirs(config.example_data_storage_location, exist_ok=True)
    makedirs(config.trained_model_storage_location, exist_ok=True)


    app.config["JSON_USE_ENCODE_METHODS"] = True
    app.run(host="0.0.0.0", load_dotenv=True)
