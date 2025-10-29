from functools import wraps
from os import path
from time import sleep

from flask_websockets import WebSocket, WebSockets

from .. import app, config

websockets = WebSockets(app)


@websockets.route("/training/status/<training_id>")  # type: ignore
def watch_training_status(ws: WebSocket, training_id: str) -> None:
    training_log = path.join(config.log_storage_location, f"{training_id}.log")
    with open(training_log, "rt") as f:
        while True:
            sleep(0.01)
            _ = ws.receive(0.01)
            line = f.readline().strip()
            if line == "finished arima model training":
                break 
            if line != "":
                ws.send(line)

    ws.close(reason="TRAINING_FINISHED")

