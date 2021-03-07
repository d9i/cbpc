#!/usr/bin/env python3
"""
Testing common files and fixtures for CBPC
Dara Kharabi for Clostra - 2021
"""

import os
import shutil
import sys
import tempfile

import pytest
import redis

# Add parent dir to path so that the cbpc folder can be found
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from cbpc import create_app  # noqa


@pytest.fixture
def app():
    """Generates an app instance with a temp DB for testing."""
    # temp directory for testing
    path = tempfile.mkdtemp()

    # create the app with test config
    test_config = {
        "TESTING": True,
        "DATABASE": "db/live.db",
        "SECRET_KEY": "testing",
        "FLASK_INSTANCE_FOLDER": path,
        "CACHE": True,
        "CACHE_HOST": "localhost",
        "CACHE_PORT": "6379",
        "CACHE_STATUS": "COLD"}

    app = create_app(test_config)

    yield app

    # flush cache after testing
    host = test_config["CACHE_HOST"]
    port = test_config["CACHE_PORT"]
    rcxn = redis.Redis(host=host, port=port, db=0)

    # clean up temp folder
    shutil.rmtree(path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
