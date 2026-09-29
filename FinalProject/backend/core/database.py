"""Database connection factory.

Provides a single ``get_connection()`` function used by every repository
to obtain a fresh MySQL connection.  Configuration values are imported
from :mod:`core.config` so that environment loading happens in one place.
"""

import mysql.connector

from core.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

DB_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME,
    # Every connection works in UTC, whatever the server's own time zone is
    # (Windows MySQL = Israel time, Docker/AWS = UTC). CURRENT_TIMESTAMP/NOW()
    # and the values we read back are all UTC; the API labels them as UTC and
    # the browser converts them to the viewer's local time.
    'time_zone': '+00:00',
}


def get_connection():
    """Return a new MySQL connection using the global config."""
    return mysql.connector.connect(**DB_CONFIG)
