# This is a unclean import but it allows to move different routes into split
# files in a Flask project which increases the maintainablility
from __main__ import app
from flask_json import as_json

@app.get("/hello-world")
@as_json
def hello_world():
    return "HEELO"