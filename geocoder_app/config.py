"""App configuration."""
from os import environ, path, urandom

from dotenv import load_dotenv

# Load variables from .env
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Set Flask configuration vars from .env file."""

    # General Config
    SECRET_KEY = environ.get("SECRET_KEY", urandom(32))
    FLASK_APP = environ.get("FLASK_APP")
    FLASK_ENV = environ.get("FLASK_ENV")
    MAPBOX_ACCESS_TOKEN = environ.get("MAPBOX_ACCESS_TOKEN")
    LOGOUT_URL = environ.get("LOGOUT_URL")
    USER_INFO_URL = environ.get("USER_INFO_URL")

    # Static Assets
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
