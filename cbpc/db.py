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


def connect_base(path=None):
    """
    DB connection wrapper.
    """
    if path is None:
        path = current_app.config["DB_PATH"]

    cxn = sqlite3.connect(path,
                          detect_types=sqlite3.PARSE_DECLTYPES
                          )

    sqlite3.register_adapter(uuid.UUID, lambda id: id.bytes_le)
    sqlite3.register_converter('UUID', lambda bytes: uuid.UUID(bytes_le=bytes))

    return cxn


def connect(path=None):
    """
    DB connection wrapper wrapper.
    Reuses one connection thoughout the lifetime of the request.
    """
    if "cxn" not in g:
        g.cxn = connect_base(path)

    return g.cxn


def setup_initial(path):
    """Create initial schema"""

    # Create the db folder if it doesn't exist
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass

    # Can't use connect() because application context doesn't exist here.
    cxn = connect_base(path)

    with cxn:
        cxn.execute('''CREATE TABLE contacts (cid UUID, date DATE)''')

    cxn.close()


def flush(path):
    """Completely empties the DB - for testing."""

    # Can't use connect() because application context doesn't exist here.
    cxn = connect_base(path)

    with cxn:
        cxn.execute('''DROP TABLE IF EXISTS contacts''')

    cxn.close()


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
        print("Database not found. Initializing at path", path)
        setup_initial(path)
