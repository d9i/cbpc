#!/usr/bin/env python3
"""
Quick n dirty script to initialize DB and prevent race conditions in production
Dara Kharabi for Clostra - 2021
"""


import os

from . import db

db_path = os.path.join(os.getcwd(), os.environ.get('FLASK_INSTANCE_FOLDER'), "db", "live.db")


if not os.path.exists(db_path):
    print("Database not found. Initializing...")
    db.setup_initial(db_path)
