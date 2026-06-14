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
}


def get_connection():
    """Return a new MySQL connection using the global config."""
    return mysql.connector.connect(**DB_CONFIG)
