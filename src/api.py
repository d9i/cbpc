#!/usr/bin/env python3
"""
CBPC API
Dara Kharabi for Clostra - 2021
"""

from datetime import datetime, timezone
from uuid import UUID

import flask
from flask import request

from db import DB

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/collect', methods=['GET'])
def collect():
    cid = request.args.get("cid")
    # Validate CID, return 400 (bad request) if it can't be turned into a UUID
    if cid is None:
        return ("\'cid\' parameter not provided.", 400)
    try:
        cid_casted = UUID(cid)
    except (TypeError, ValueError):
        return ("UUID incorrectly formatted, please try again.", 400)

    # If CID is valid, store it in db
    row = (
        cid_casted,
        datetime.now(timezone.utc)
    )

    cxn = db_live.connect()
    with cxn:
        # perform DB operations, then commit
        cxn.execute('''INSERT INTO contacts VALUES (?, ?)''', row)

    cxn.close()

    return ("", 200)  # return empty response


db_live = DB("db/live.db")
app.run()
