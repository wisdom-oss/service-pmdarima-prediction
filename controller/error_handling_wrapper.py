from functools import wraps
from flask import jsonify, request

def check_for_empty_json_fields(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.json
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Check if any value is None
        if any(value is None for value in data.values()):
            return jsonify({"error": "Null or undefined value found in request"}), 400

        return f(*args, **kwargs)
    return decorated_function