"""Initialize Flask Application."""
from flask import Flask


def create_app():
    """Construct the core application."""
    app = Flask(__name__)
    app.config.from_object("config.Config")

    with app.app_context():
        from . import routes  # noqa: F401

        return app
