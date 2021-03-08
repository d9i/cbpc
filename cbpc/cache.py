#!/usr/bin/env python3
"""
CBPC SQLite Redis cache helper
Dara Kharabi for Clostra - 2021
"""

from datetime import date, timedelta
import time

import redis
from flask import current_app, g


def connect():
    """
    Cache connection wrapper.
    Reuses one connection thoughout the lifetime of the request.
    """
    host = current_app.config["CACHE_HOST"]
    port = current_app.config["CACHE_PORT"]

    if "rcxn" not in g:
        g.rcxn = redis.Redis(host=host, port=port, db=0)

    return g.rcxn


def close_cxn(e=None):
    """Unbinds active connection if one exists"""
    g.pop("rcxn", None)


def pfaddex(k, v, exp=None):
    """Wrapper for redis PFADD. Takes care of expiration"""
    if exp is None:
        exp = timedelta(days=current_app.config["CACHE_EXP_DAYS"])
    rcxn = connect()

    # Add to cache, set expiration
    rcxn.pfadd(k, v)
    ret_exp = rcxn.expire(k, exp)
    if ret_exp is True:
        return True
    else:
        return False


def app_init(app) -> None:
    """Register cache hooks with flask."""

    # Tell flask to close cache cxn on request end
    app.teardown_appcontext(close_cxn)

    # wait until redis connects - useful for when flask boots before redis
    connected = False
    print("Connecting to Redis cache...", end="")
    while not connected:
        host = app.config["CACHE_HOST"]
        port = app.config["CACHE_PORT"]

        rcxn = redis.Redis(host=host, port=port, db=0)
        try:
            rcxn.ping()
            connected = True
            print("Connected!")
        except redis.ConnectionError:
            time.sleep(0.2)
            print(".", end="")
