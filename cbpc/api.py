#!/usr/bin/env python3
"""
CBPC API
Dara Kharabi for Clostra - 2021
"""

from datetime import date, datetime, time, timedelta, timezone, tzinfo
from uuid import UUID

from dateutil.parser import isoparse
from flask import Blueprint, request

from . import cache

bp = Blueprint('api', __name__)


@bp.route('/collect', methods=['GET'])
def collect():
    """
    Given a valid UUID 'cid,' record it and the current GMT date.
    Optional parameter 'd' can override the current date with a custom one,
    for generating test data.
    """

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

    # If CID is valid and not store it in redis cache
    # stringify both date and cid
    cid_casted = str(cid_casted)
    d_casted = d_casted.isoformat()
    ret = cache.pfaddex(d_casted, cid_casted)
    if ret is True:
        return ("", 200)  # return empty response
    else:
        # if cache operation failed
        return ("Internal Server error", 500)


def isTzAware(dt):
    """returns true if the given date is timezone-aware"""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return False
    else:
        return True


def uniques(start: date, end: date = None) -> int:
    """Gives count of unique cids between dates (inclusive)"""
    if end is None:
        end = start
    rcxn = cache.connect()

    # Get keys for each day in range
    delta = end - start
    keys = [(start + timedelta(days=d)).isoformat() for d in range(delta.days + 1)]

    # Pull from cache
    return rcxn.pfcount(*keys)


def validate_date(dateStr):
    """
    Parse and validate a date string for daily and monthly uniques.

    Returns a tuple, where the first value is a boolean indicating success.
    If successful, the second value will contain the parsed date. Otherwise,
    it will contain an error and return code.
    """

    if dateStr is None:
        return (False, ("\'d\' parameter not provided.\n", 400))

    # Error if date cannot be parsed
    try:
        d_casted = isoparse(dateStr)
    except ValueError as e:
        return (False, ("ISO 8601 timestamp incorrectly formatted, please try again.\n", 400))

    # Error if no date given
    if isinstance(d_casted, time):
        return (False, ("ISO 8601 timestamp requires a date, please try again.\n", 400))

    # Truncate datetimes to dates
    if isinstance(d_casted, datetime):
        # If a timezone aware time is given, convert to UTC before truncating
        if isTzAware(d_casted):
            d_casted = d_casted.astimezone(tz=timezone.utc)
        d_casted = d_casted.date()

    # Ignore queries older than 60 days
    if (date.today() - d_casted).days > 60:
        return (False, ("Query period out of range.\n", 400))

    return (True, d_casted)


@bp.route('/daily_uniques', methods=['GET'])
def daily_uniques():
    """Given a GMT date d, return the # of unique cids from that day"""

    d = request.args.get("d")
    status, value = validate_date(d)

    # Error if validation failed, else pass on the value
    if status is False:
        return value
    else:
        d_casted = value

    # pull value from redis
    cnt = uniques(d_casted)

    # API return value must be a string
    cnt_casted = str(cnt)

    return (cnt_casted, 200)


@bp.route('/monthly_uniques', methods=['GET'])
def monthly_uniques():
    """
    Given a GMT date d, return the # of unique cids month-to-date for that day
    """

    d = request.args.get("d")
    status, value = validate_date(d)

    # Error if validation failed, else pass on the value
    if status is False:
        return value
    else:
        d_casted = value

    start = d_casted.replace(day=1)

    cnt = uniques(start, d_casted)

    # API return value must be a string
    cnt_casted = str(cnt)

    return (cnt_casted, 200)
