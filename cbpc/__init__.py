#!/usr/bin/env python3
"""
CBPC Backend main file
Dara Kharabi for Clostra - 2021
"""

import os

from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""

    # Get Flask instance folder
    if test_config is not None:
        abs_instance_path = test_config["FLASK_INSTANCE_FOLDER"]
    else:
        abs_instance_path = os.path.join(os.getcwd(), os.environ.get('FLASK_INSTANCE_FOLDER'))

    # Instantiate Flask app
    app = Flask(__name__, instance_path=abs_instance_path, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_envvar('FLASK_CFG')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Create the instance folder if it doesn't exist
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
    from . import db
    db.app_init(app)

    # apply the blueprints to the app
    from . import api
    app.register_blueprint(api.bp)

    print("CBPC App thread started.")

    return app
