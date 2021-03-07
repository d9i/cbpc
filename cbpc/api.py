#!/usr/bin/env python3
"""
CBPC API
Dara Kharabi for Clostra - 2021
"""

from datetime import datetime, time, timezone, tzinfo
from uuid import UUID

from dateutil.parser import isoparse
from flask import Blueprint, request

from . import db
from . import cache

bp = Blueprint('api', __name__)


@bp.route('/collect', methods=['GET'])
def collect():
    print("Collect received")
    cid, d = request.args.get("cid"), request.args.get("d")
    # Validate CID, return 400 (bad request) if it can't be turned into a UUID
    if cid is None:
        return ("\'cid\' parameter not provided.\n", 400)
    try:
        cid_casted = UUID(cid)
    except (TypeError, ValueError):
        return ("UUID incorrectly formatted, please try again.\n", 400)

    if d is None:
        d_casted = datetime.now(timezone.utc).date()
    else:
        # Validate date if given, return 400 (bad request) if it fails
        try:
            d = float(d)
            d_casted = datetime.fromtimestamp(d, tz=timezone.utc).date()
        except (ValueError, OverflowError):
            return ("Date timestamp incorrectly formatted or out of range, please try again.\n", 400)

    # If CID is valid and not cached, store it in db
    row = (cid_casted, d_casted)
    # Caching
    if cache.cache("collect", row):
        return ("", 200)  # no need to record in DB, cache has it covered

    cxn = db.connect()
    with cxn:
        # perform DB operations, then commit
        cxn.execute('''INSERT INTO contacts VALUES (?, ?)''', row)

    return ("", 200)  # return empty response


def isTzAware(dt):
    """returns true if the given date is timezone-aware"""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return False
    else:
        return True


def uniques(start: datetime, end: datetime) -> int:
    """Gives count of unique cids between datetimes (inclusive)"""
    start = datetime.combine(start.date(), time.min, tzinfo=timezone.utc)
    end = datetime.combine(end.date(), time.max, tzinfo=timezone.utc)

    cxn = db.connect()
    with cxn:
        cur = cxn.cursor()
        # perform DB operations, then commit
        cur.execute(
            '''SELECT COUNT(DISTINCT cid) FROM contacts WHERE date BETWEEN ? AND ?''',
            (start.isoformat(sep=" "), end.isoformat(sep=" "))
        )
        out = cur.fetchone()[0]

    return out


@bp.route('/daily_uniques', methods=['GET'])
def daily_uniques():
    d = request.args.get("d")
    try:
        d_casted = isoparse(d)
    except ValueError:
        return ("ISO 8601 timestamp incorrectly formatted, please try again.\n", 400)

    # Error if no date given
    if isinstance(d_casted, time):
        return ("ISO 8601 timestamp requires a date, please try again.\n", 400)

    # Ignore queries older than 60 days
    if (datetime.now() - d_casted).days > 60:
        return ("Query period out of range.\n", 400)

    # Truncate datetimes to dates
    if isinstance(d_casted, datetime):
        # If a timezone aware time is given, convert to UTC before truncating
        if isTzAware(d_casted):
            d_casted = d_casted.astimezone(tz=timezone.utc)
        d_casted = d_casted.date()

    cnt = uniques(d_casted, d_casted)

    # API return value must be a string
    cnt_casted = str(cnt)

    return (cnt_casted, 200)


@bp.route('/monthly_uniques', methods=['GET'])
def monthly_uniques():
    d = request.args.get("d")
    try:
        d_casted = isoparse(d)
    except ValueError:
        return ("ISO 8601 timestamp incorrectly formatted, please try again.\n", 400)

    # Error if no date given
    if isinstance(d_casted, time):
        return ("ISO 8601 timestamp requires a date, please try again.\n", 400)

    # Ignore queries older than 60 days
    if (datetime.now() - d_casted).days > 60:
        return ("Query period out of range.\n", 400)

    # Truncate datetimes to dates
    if isinstance(d_casted, datetime):
        # If a timezone aware time is given, convert to UTC before truncating
        if isTzAware(d_casted):
            d_casted = d_casted.astimezone(tz=timezone.utc)
        d_casted = d_casted.date()

    start = d_casted.replace(day=1)

    cnt = uniques(start, d_casted)

    # API return value must be a string
    cnt_casted = str(cnt)

    return (cnt_casted, 200)
