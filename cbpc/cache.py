#!/usr/bin/env python3
"""
CBPC SQLite Redis cache helper
Dara Kharabi for Clostra - 2021
"""

from flask import current_app, g
import redis


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
    """Closes active connection if one exists"""
    rcxn = g.pop("rcxn", None)

    if rcxn is not None:
        rcxn.close()


def cache(type, v):

    if type == "collect":
        cid, d = v
        # if
        pass
    elif type == "daily":
        d = v
        pass
    else:
        raise Exception("incorrect caching type given")


def warm_cache():
    host = current_app.config["CACHE_HOST"]
    port = current_app.config["CACHE_PORT"]

    rcxn = redis.Redis(host=host, port=port, db=0)


def app_init(app, suppress_db_init=False) -> None:
    """Register db hooks with flask and create db if needed."""

    # Tell flask to close cache cxn on request end
    app.teardown_appcontext(close_cxn)

    # Warm cache with DB data if not warm
    if current_app.config["CACHE_STATUS"] == "COLD":
        current_app.config["CACHE_STATUS"] = "WARMING"
        warm_cache()
