from .. import app, config
from contextlib import redirect_stdout
from os import path
from threading import Thread
from time import sleep
from flask_websockets import WebSocket, WebSockets
import sys

websockets = WebSockets(app)


@websockets.route("/training/status/<training_id>")
def watch_training_status(ws: WebSocket, training_id: str) -> None:
    t = Thread(
        target=listen_to_training_updates, kwargs={"training_id": training_id, "ws": ws}
    )
    t.start()
    with websockets.subscribe(ws, [training_id]):
        for _ in ws.iter_text():
            pass


def listen_to_training_updates(training_id: str, ws: WebSocket) -> None:
    training_log = path.join(config.log_storage_location, f"{training_id}.log")
    with open(training_log, "rt") as f:
        while True:
            sleep(0.1)
            line = f.readline().strip()
            if line == "":
                continue
            if line == "finished arima model training":
                ws.close(reason="training finished")
                break
            websockets.publish(line, [training_id])
