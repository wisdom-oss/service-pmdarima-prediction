from os import makedirs

import pmdarima_prediction
from pmdarima_prediction import Settings

config = Settings()
if not config.use_s3_storage:
    makedirs(config.result_storage_location, exist_ok=True)
    makedirs(config.example_data_storage_location, exist_ok=True)
    makedirs(config.trained_model_storage_location, exist_ok=True)
    makedirs(config.log_storage_location, exist_ok=True)

pmdarima_prediction.app.run(host="0.0.0.0", port=8000, debug=True)
