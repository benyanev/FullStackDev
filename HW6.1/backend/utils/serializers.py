"""Serialization helpers for converting database records to JSON-safe dicts.

The ``serialize_dates`` / ``serialize_dates_list`` helpers replace the
repeated ``isinstance(…, datetime)`` checks that were scattered across
every route handler in the old monolithic ``app.py``.
"""

from datetime import datetime


def serialize_dates(record, *fields):
    """Convert *datetime* values to ISO-8601 strings **in-place**.

    Args:
        record: A single dict (database row).
        *fields: Names of keys whose values should be converted.

    Returns:
        The same dict with datetime fields replaced by strings,
        or ``None`` if *record* is ``None``.
    """
    if record is None:
        return record
    for field in fields:
        if isinstance(record.get(field), datetime):
            record[field] = record[field].isoformat()
    return record


def serialize_dates_list(records, *fields):
    """Convert *datetime* values to ISO-8601 strings for a list of dicts.

    Args:
        records: A list of dicts (database rows).
        *fields: Names of keys whose values should be converted.

    Returns:
        The same list with datetime fields replaced by strings.
    """
    for record in records:
        serialize_dates(record, *fields)
    return records
