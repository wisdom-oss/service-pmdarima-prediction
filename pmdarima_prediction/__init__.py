from flask import Flask
from werkzeug.exceptions import HTTPException

from .exceptions import ServiceException
from .settings import Settings

config = Settings()  # pyright:ignore reportCallIssue

app = Flask(__name__)

from .routes import *  # noqa: E402, F403
