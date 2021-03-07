#!/usr/bin/env python3
"""
API tests
Dara Kharabi for Clostra - 2021
"""

import random
from string import printable
from uuid import uuid4
from datetime import date, datetime, time, timedelta, timezone

import pytest


@pytest.mark.parametrize(('endpoint'),
                         ["/", "/colect", "/h25h1"] +
                         ["/" + "".join(((random.choice(printable) for i in range(random.randint(1, 50)))))]
                         )
def test_notFound(client, endpoint):
    """Does the API properly handle unimplemented endpoints?"""

    resp = client.get(endpoint)
    assert resp.status_code == 404


def test_collect_happy_path(client):
    """Does the API properly collect a well-formatted UUID?"""

    resp = client.get(f"/collect?cid={str(uuid4())}")
    assert resp.data == b""
    assert resp.status_code == 200


def test_collect_happy_path_date(client):
    """Does the API properly collect a well-formatted UUID with custom Unix timestamp?"""

    resp = client.get(f"/collect?cid={str(uuid4())}&d=1615000000")
    assert resp.data == b""
    assert resp.status_code == 200


def test_collect_bad_cid(client):
    """Does the API error if given a bad UUID?"""

    resp = client.get(f"/collect?cid={str(uuid4())[random.randint(1,5):]}")
    assert resp.status_code == 400


@pytest.mark.parametrize(('date'),
                         ["2020-09-31", "2020-121-23", "2021-01-01T55:12:12", "asdf"]
                         )
def test_collect_bad_date(client, date):
    """Does the API error if given a bad custom Unix timestamp?"""

    resp = client.get(f"/collect?cid={str(uuid4())}&d={date}")
    assert resp.status_code == 400


def test_empty_daily(client):
    """
    Does the API return 0 when asked for daily uniques without collecting anything?
    This is important for testing the statelessness of the test fixture.
    """

    resp = client.get(f"/daily_uniques?d={date.today()}")
    assert resp.data == b"0"
    assert resp.status_code == 200


def test_empty_monthly(client):
    """
    Does the API return 0 when asked for monthly uniques without collecting anything?
    This is important for testing the statelessness of the test fixture.
    """
    resp = client.get(f"/monthly_uniques?d={date.today()}")
    assert resp.data == b"0"
    assert resp.status_code == 200


def test_functional_daily(client):
    """
    A functional test of the daily_uniques endpoint. 
    Collects both unique and repeating cids, then looks for a reasonably
    accurate result
    """
    yyday = date.today() - timedelta(days=2)
    yyday_ts = datetime.combine(yyday, time.min, tzinfo=timezone.utc).timestamp()

    for i in range(1000):
        cid = uuid4()
        resp = client.get(f"/collect?cid={cid}")
        assert resp.data == b""
        assert resp.status_code == 200

    # Running this test case at midnight GMT may have unexpected results
    resp = client.get(f"/daily_uniques?d={date.today()}")
    assert abs(int(resp.data) - 1000) < 8
    assert resp.status_code == 200

    cid = uuid4()
    for i in range(1000):
        if i < 501:
            cid = uuid4()
        resp = client.get(f"/collect?cid={cid}&d={yyday_ts}")
        assert resp.data == b""
        assert resp.status_code == 200

    # Just making sure the results haven't changed with the new data
    resp = client.get(f"/daily_uniques?d={date.today()}")
    assert abs(int(resp.data) - 1000) < 8
    assert resp.status_code == 200

    resp = client.get(f"/daily_uniques?d={yyday}")
    assert abs(int(resp.data) - 501) < 6
    assert resp.status_code == 200


def test_functional_monthly(client):
    """
    A functional test of the monthly_uniques endpoint. Collects both unique 
    and repeating cids, then looks for the correct results.
    """
    yyday = date.today() - timedelta(days=2)
    yyday_ts = datetime.combine(yyday, time.min, tzinfo=timezone.utc).timestamp()
    tomorrow = date.today() + timedelta(days=1)

    for i in range(1000):
        cid = uuid4()
        resp = client.get(f"/collect?cid={cid}")
        assert resp.data == b""
        assert resp.status_code == 200

    resp = client.get(f"/monthly_uniques?d={date.today()}")
    assert abs(int(resp.data) - 1000) < 1
    assert resp.status_code == 200

    cid = uuid4()
    for i in range(1000):
        if i < 501:
            cid = uuid4()
        resp = client.get(f"/collect?cid={cid}&d={yyday_ts}")
        assert resp.data == b""
        assert resp.status_code == 200

    resp = client.get(f"/monthly_uniques?d={date.today()}")
    assert abs(int(resp.data) - 1501) < 1
    assert resp.status_code == 200

    resp = client.get(f"/monthly_uniques?d={yyday}")
    assert abs(int(resp.data) - 501) < 1
    assert resp.status_code == 200

    resp = client.get(f"/monthly_uniques?d={tomorrow}")
    assert abs(int(resp.data) - 1501) < 1
    assert resp.status_code == 200
