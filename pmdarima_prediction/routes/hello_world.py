from .. import app
from flask_json import as_json


@app.get("/hello-world")
@as_json
def hello_world():
    return "HEELO"
