from flask_json import as_json  # type: ignore

from .. import app


@app.get("/hello-world")
@as_json
def hello_world():
    return "HEELO"
