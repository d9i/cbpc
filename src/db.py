#!/usr/bin/env python3
"""
CBPC SQLite DB helper
Dara Kharabi for Clostra - 2021
"""

import os
import sqlite3
import uuid


class DB:
    def __init__(self, path, suppress_db_init=False) -> None:
        self.path = path

        if not os.path.exists(path) and not suppress_db_init:
            print("Database not found. Initializing...")
            self.setup_initial()

    def setup_initial(self):
        """Create initial schema"""

        cxn = self.connect()

        with cxn:
            cxn.execute('''CREATE TABLE contacts (cid UUID, date TIMESTAMP)''')

        cxn.close()

    def connect(self):
        """
        DB connection wrapper. 
        This is helpful because it avoids repeating path and registering 
        adapters/converters elsewhere in the codebase.
        """

        cxn = sqlite3.connect(self.path)

        sqlite3.register_adapter(uuid.UUID, lambda id: id.bytes_le)
        sqlite3.register_converter('UUID', lambda bytes: uuid.UUID(bytes_le=bytes))

        return cxn
