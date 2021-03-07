#!/usr/bin/env python3
"""
CBPC SQLite Redis cache helper
Dara Kharabi for Clostra - 2021
"""

from datetime import date, timedelta

import redis
from flask import current_app, g

from . import db


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
    """Interface for caching, used across routes"""
    rcxn = connect()

    if type == "collect":
        cid, d = v
        # stringify both date and cid
        cid = str(cid)
        d = d.isoformat()
        rcxn.pfadd(d, cid)
        # TODO: Add caching for collect requests with invalidation at 00:00 GMT
        return None
    elif type == "daily":
        d = v.isoformat()
        if current_app.config["CACHE_STATUS"] == "WARM":
            return rcxn.pfcount(d)
        else:
            return None
    else:
        raise Exception("incorrect caching type given")


def warm_cache(app):
    """Warms cache by filling HLL datastructures from database"""

    print("Warming Redis cache...")
    host = app.config["CACHE_HOST"]
    port = app.config["CACHE_PORT"]
    db_path = app.config["DB_PATH"]

    cxn = db.connect_base(db_path)
    rcxn = redis.Redis(host=host, port=port, db=0)

    # Flush cache to ensure it's fresh
    rcxn.flushdb()

    cur = cxn.cursor()
    # datelimit is set to 100 days to allow for MtD queries 60 days back
    date_limit = (date.today() - timedelta(days=100)).isoformat()
    cur.execute("SELECT cid, date FROM contacts WHERE date > ?", [date_limit])
    res = cur.fetchmany()
    while res != []:
        for row in res:
            cid, d = str(row[0]), row[1].isoformat()
            rcxn.pfadd(d, cid)
        res = cur.fetchmany()

    app.config["CACHE_STATUS"] = "WARM"
    print("Redis cache warmed.")


def app_init(app, suppress_db_init=False) -> None:
    """Register db hooks with flask and create db if needed."""

    # Tell flask to close cache cxn on request end
    app.teardown_appcontext(close_cxn)

    # Warm cache with DB data if not warm
    if app.config["CACHE_STATUS"] == "COLD":
        app.config["CACHE_STATUS"] = "WARMING"
        warm_cache(app)
