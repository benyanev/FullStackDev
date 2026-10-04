"""Unit tests for utils.serializers — AAA pattern."""

from datetime import datetime, timezone

from utils.serializers import serialize_dates, serialize_dates_list


def test_datetime_becomes_utc_iso_string():
    # Arrange — MySQL returns naive datetimes; our connections run in UTC
    row = {"id": 1, "created_at": datetime(2026, 9, 29, 0, 40, 7)}

    # Act
    serialize_dates(row, "created_at")

    # Assert — explicitly UTC, so a browser in Israel shows 03:40 local time
    assert row["created_at"] == "2026-09-29T00:40:07+00:00"
    parsed = datetime.fromisoformat(row["created_at"])
    assert parsed.tzinfo == timezone.utc


def test_non_datetime_and_none_are_left_alone():
    # Arrange
    row = {"created_at": "already a string"}

    # Act / Assert
    assert serialize_dates(row, "created_at")["created_at"] == "already a string"
    assert serialize_dates(None, "created_at") is None


def test_serialize_list():
    # Arrange
    rows = [{"t": datetime(2026, 1, 1)}, {"t": datetime(2026, 1, 2)}]

    # Act
    serialize_dates_list(rows, "t")

    # Assert
    assert [r["t"] for r in rows] == ["2026-01-01T00:00:00+00:00", "2026-01-02T00:00:00+00:00"]
