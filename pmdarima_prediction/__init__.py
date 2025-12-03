# isort: skip_file

from os import makedirs

from flask import Flask

from .settings import Settings

config = Settings()  # pyright:ignore reportCallIssue
makedirs(config.log_storage_location, exist_ok=True)

app = Flask(__name__)

from .handlers import *  # noqa: E402, F403
from .routes import *  # noqa: E402, F403
