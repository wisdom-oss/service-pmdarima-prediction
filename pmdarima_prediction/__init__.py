from flask import Flask
from .settings import Settings

config = Settings()

app = Flask(__name__)

from .routes import *
