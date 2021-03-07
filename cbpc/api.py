#!/usr/bin/env python3
"""
CBPC API
Dara Kharabi for Clostra - 2021
"""

from dateutil.parser import isoparse

from datetime import datetime, time, timezone
from uuid import UUID

from flask import Blueprint, request

from . import db

bp = Blueprint('api', __name__)


@bp.route('/collect', methods=['GET'])
def collect():
    cid, d = request.args.get("cid"), request.args.get("d")
    # Validate CID, return 400 (bad request) if it can't be turned into a UUID
    if cid is None:
        return ("\'cid\' parameter not provided.", 400)
    try:
        cid_casted = UUID(cid)
    except (TypeError, ValueError):
        return ("UUID incorrectly formatted, please try again.", 400)

    if d is None:
        d_casted = datetime.now(timezone.utc)
    else:
        # Validate date if given, return 400 (bad request) if it fails
        try:
            d = int(d)
            d_casted = datetime.fromtimestamp(d, tz=timezone.utc)
        except (ValueError, OverflowError):
            return ("Date timestamp incorrectly formatted or out of range, please try again.", 400)

    # If CID is valid, store it in db
    row = (cid_casted, d_casted)

    cxn = db.connect()
    with cxn:
        # perform DB operations, then commit
        cxn.execute('''INSERT INTO contacts VALUES (?, ?)''', row)

    return ("", 200)  # return empty response


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
        print(out)

    return out


@bp.route('/daily_uniques', methods=['GET'])
def daily_uniques():
    d = request.args.get("d")
    try:
        d_casted = isoparse(d)
    except ValueError:
        return ("ISO 8601 timestamp incorrectly formatted, please try again.", 400)

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
        return ("ISO 8601 timestamp incorrectly formatted, please try again.", 400)

    start = d_casted.replace(day=1)

    cnt = uniques(start, d_casted)

    # API return value must be a string
    cnt_casted = str(cnt)

    return (cnt_casted, 200)
