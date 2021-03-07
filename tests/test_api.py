#!/usr/bin/env python3
"""
API tests
Dara Kharabi for Clostra - 2021
"""

import random
from string import printable
from uuid import uuid4

import pytest


@pytest.mark.parametrize(('endpoint'),
                         ["/", "/colect", "/h25h1"] +
                         ["/" + "".join(((random.choice(printable) for i in range(random.randint(1, 50)))))]
                         )
def test_notFound(client, endpoint):
    resp = client.get(endpoint)
    assert resp.status_code == 404


def test_collect_happy_path(client):
    resp = client.get(f"/collect?cid={str(uuid4())}")
    assert resp.data == b""
    assert resp.status_code == 200


def test_collect_happy_path_date(client):
    resp = client.get(f"/collect?cid={str(uuid4())}&d=1615000000")
    assert resp.data == b""
    assert resp.status_code == 200


def test_collect_bad_cid(client):
    resp = client.get(f"/collect?cid={str(uuid4())[random.randint(1,5):]}")
    assert resp.status_code == 400


def test_collect_happy_bad_date(client):
    resp = client.get(f"/collect?cid={str(uuid4())}&d=2020-09-31")
    assert resp.status_code == 400
