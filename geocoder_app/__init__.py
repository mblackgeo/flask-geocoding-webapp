"""Initialize Flask Application."""
from flask import Flask

__version__ = "0.0.1"
__all__ = ["__version__", "create_app"]


def create_app() -> Flask:
    """Construct the core application."""
    app = Flask(__name__)
    app.config.from_object("geocoder_app.config.Config")

    with app.app_context():
        from . import routes  # noqa: F401

        return app
