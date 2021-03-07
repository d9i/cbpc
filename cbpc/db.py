#!/usr/bin/env python3
"""
CBPC SQLite DB helper
Dara Kharabi for Clostra - 2021
"""

import os
import sqlite3
import uuid
from os.path import abspath

from flask import current_app, g


def setup_initial(path):
    """Create initial schema"""

    # Create the db folder if it doesn't exist
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass

    # Can't use connect() because application context doesn't exist here.
    # Not registering adapters/converters for this query because no
    # inserts/selects are being used.
    cxn = sqlite3.connect(path,
                          detect_types=sqlite3.PARSE_DECLTYPES
                          )

    with cxn:
        cxn.execute('''CREATE TABLE contacts (cid UUID, date TIMESTAMP)''')

    cxn.close()


def flush(path):
    """Completely empties the DB - for testing."""

    # Can't use connect() because application context doesn't exist here.
    # Not registering adapters/converters for this query because no
    # inserts/selects are being used.
    cxn = sqlite3.connect(path,
                          detect_types=sqlite3.PARSE_DECLTYPES
                          )

    with cxn:
        cxn.execute('''DROP TABLE IF EXISTS contacts''')

    cxn.close()


def connect(path=None):
    """
    DB connection wrapper.
    Reuses one connection thoughout the lifetime of the request.
    """
    if path is None:
        path = current_app.config["DB_PATH"]

    if "cxn" not in g:
        g.cxn = sqlite3.connect(path,
                                detect_types=sqlite3.PARSE_DECLTYPES
                                )

        sqlite3.register_adapter(uuid.UUID, lambda id: id.bytes_le)
        sqlite3.register_converter('UUID', lambda bytes: uuid.UUID(bytes_le=bytes))

    return g.cxn


def close_cxn(e=None):
    """Closes active connection if one exists"""
    cxn = g.pop("cxn", None)

    if cxn is not None:
        cxn.close()


def app_init(app, suppress_db_init=False) -> None:
    """Register db hooks with flask and create db if needed."""

    # Tell flask to close db cxn on request end
    app.teardown_appcontext(close_cxn)

    path = os.path.join(app.instance_path, app.config["DATABASE"])
    app.config["DB_PATH"] = path

    if not os.path.exists(path) and not suppress_db_init:
        print("Database not found. Initializing...")
        setup_initial(path)
