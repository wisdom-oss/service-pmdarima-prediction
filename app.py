from os import makedirs

import pmdarima_prediction
from pmdarima_prediction import Settings

config = Settings()
makedirs(config.log_storage_location, exist_ok=True)

pmdarima_prediction.app.run(host="0.0.0.0", port=8000, debug=False)
