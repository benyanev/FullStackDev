"""Request parsing helpers shared by all controllers.

They make every endpoint robust against unexpected input, so a bad request
gets a clear 400 instead of crashing with a 500:
- a body that is missing, not JSON, or not an object (``null``, ``[1]``)
- a field with the wrong type (``{"name": 5}``)
- negative or huge pagination parameters (``?_limit=-1`` / ``?_limit=100000``)
"""

from flask import request


def json_body():
    """Return the request's JSON object, or ``{}`` if there isn't a valid one."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def get_text(data, key):
    """Return ``data[key]`` stripped if it is a string, otherwise ``''``."""
    value = data.get(key)
    return value.strip() if isinstance(value, str) else ''


def page_params(default_limit=10, max_limit=50):
    """Read ``_start`` / ``_limit`` from the query string, clamped to safe values.

    Returns:
        A tuple ``(start, limit)`` with ``start >= 0`` and
        ``1 <= limit <= max_limit``.
    """
    start = request.args.get('_start', 0, type=int)
    limit = request.args.get('_limit', default_limit, type=int)
    return max(0, start), min(max(1, limit), max_limit)
