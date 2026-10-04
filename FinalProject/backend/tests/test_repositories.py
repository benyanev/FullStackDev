"""Unit tests for the repository layer — no real database needed.

``get_connection`` is replaced with a MagicMock connection, so each test
checks the repository's own logic:

- it runs a query and returns the right thing from the cursor
  (``fetchone`` / ``fetchall`` / ``rowcount`` / ``lastrowid``),
- it commits only when it writes,
- it ALWAYS closes the cursor and the connection (the ``finally`` block).

Most functions follow the same pattern, so they are covered by one
table-driven test; functions with extra logic get their own tests below.
"""

import importlib
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

ROW = {"id": 1, "name": "Row"}
ROWS = [ROW, {"id": 2, "name": "Row 2"}]
WHEN = datetime(2099, 1, 1)

# How each kind of function reads its result from the cursor:
#   kind        → (cursor setup,                    expected return, writes?)
KINDS = {
    "fetchone": ({"fetchone": ROW}, ROW, False),
    "fetchall": ({"fetchall": ROWS}, ROWS, False),
    "count":    ({"fetchone": (7,)}, 7, False),
    "exists":   ({"fetchone": (1,)}, True, False),
    "insert":   ({"lastrowid": 99}, 99, True),
    "changed":  ({"rowcount": 1}, True, True),
    "deleted":  ({"rowcount": 3}, 3, True),
    "write":    ({}, None, True),
}

# (repository module, function, args, kind)
CASES = [
    ("comment_repository", "create_comment", (1, 2, "Hi", None), "insert"),
    ("comment_repository", "get_comments_by_post", (1,), "fetchall"),

    ("follow_repository", "follow_user", (1, 2), "changed"),
    ("follow_repository", "unfollow_user", (1, 2), "changed"),
    ("follow_repository", "is_following", (1, 2), "exists"),
    ("follow_repository", "get_followers_count", (1,), "count"),
    ("follow_repository", "get_following_count", (1,), "count"),
    ("follow_repository", "get_followers", (1,), "fetchall"),
    ("follow_repository", "get_following", (1,), "fetchall"),

    ("like_repository", "add_like", (1, 2), "changed"),
    ("like_repository", "remove_like", (1, 2), "changed"),
    ("like_repository", "get_like_count", (2,), "count"),
    ("like_repository", "has_user_liked", (1, 2), "exists"),

    ("post_repository", "get_post_by_id", (1,), "fetchone"),
    ("post_repository", "create_post", (1, "Title", "<p>Body</p>", "", "/v.mp4"), "insert"),
    ("post_repository", "delete_post", (1,), "changed"),
    ("post_repository", "get_following_posts_paginated", (1, 0, 10), "fetchall"),

    ("report_repository", "create_report", (1, 2, "Spam"), "changed"),
    ("report_repository", "get_pending_reports", (), "fetchall"),
    ("report_repository", "update_report_status", (1, "dismissed"), "changed"),

    ("reset_repository", "create_reset_token", (1, "a" * 64, WHEN), "insert"),
    ("reset_repository", "get_reset_by_token", ("a" * 64,), "fetchone"),
    ("reset_repository", "mark_token_used", ("a" * 64,), "changed"),
    ("reset_repository", "invalidate_user_tokens", (1,), "write"),

    ("session_repository", "get_session", ("uuid",), "fetchone"),
    ("session_repository", "delete_session", ("uuid",), "write"),
    ("session_repository", "delete_user_sessions", (1,), "deleted"),
    ("session_repository", "delete_expired_sessions", (), "deleted"),

    ("user_repository", "get_user_by_id", (1,), "fetchone"),
    ("user_repository", "get_user_by_email", ("a@b.com",), "fetchone"),
    ("user_repository", "get_users_paginated", (0, 10), "fetchall"),
    ("user_repository", "create_user", ("Ann", "a@b.com", "hash"), "insert"),
    ("user_repository", "update_password_hash", (1, "hash"), "changed"),
    ("user_repository", "set_user_role", (1, "admin"), "changed"),
    ("user_repository", "create_agent", ("Bot", "b@x", "hash", "bio", "grumpy"), "insert"),
    ("user_repository", "get_active_agents", (), "fetchall"),
]


@pytest.fixture()
def fake_db():
    """Return a factory that patches get_connection in a repository module."""
    patchers = []

    def _connect(module_name, **cursor_setup):
        conn = MagicMock()
        cursor = conn.cursor.return_value
        if "fetchone" in cursor_setup:
            cursor.fetchone.return_value = cursor_setup["fetchone"]
        if "fetchall" in cursor_setup:
            cursor.fetchall.return_value = cursor_setup["fetchall"]
        cursor.rowcount = cursor_setup.get("rowcount", 0)
        cursor.lastrowid = cursor_setup.get("lastrowid")

        patcher = patch(f"repositories.{module_name}.get_connection", return_value=conn)
        patcher.start()
        patchers.append(patcher)
        return conn, cursor

    yield _connect
    for patcher in patchers:
        patcher.stop()


def _call(module_name, func_name, *args, **kwargs):
    module = importlib.import_module(f"repositories.{module_name}")
    return getattr(module, func_name)(*args, **kwargs)


# ---------------------------------------------------------------------------
# Table-driven: every simple repository function
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "module_name, func_name, args, kind", CASES,
    ids=[f"{m}.{f}" for m, f, _, _ in CASES],
)
def test_repository_function(fake_db, module_name, func_name, args, kind):
    # Arrange
    cursor_setup, expected, writes = KINDS[kind]
    conn, cursor = fake_db(module_name, **cursor_setup)

    # Act
    result = _call(module_name, func_name, *args)

    # Assert
    assert result == expected
    cursor.execute.assert_called_once()
    assert conn.commit.called == writes
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


# ---------------------------------------------------------------------------
# Functions with extra logic
# ---------------------------------------------------------------------------
def test_connection_closed_even_when_query_fails(fake_db):
    # Arrange
    conn, cursor = fake_db("post_repository")
    cursor.execute.side_effect = RuntimeError("DB down")

    # Act & Assert
    with pytest.raises(RuntimeError):
        _call("post_repository", "get_post_by_id", 1)
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


def test_count_returns_int_not_bool(fake_db):
    # Arrange
    fake_db("follow_repository", fetchone=(0,))

    # Act / Assert
    assert _call("follow_repository", "get_followers_count", 1) == 0


def test_exists_false_when_no_row(fake_db):
    # Arrange
    fake_db("like_repository", fetchone=None)

    # Act / Assert
    assert _call("like_repository", "has_user_liked", 1, 2) is False


def test_changed_false_when_no_rows_affected(fake_db):
    # Arrange — e.g. INSERT IGNORE of a duplicate like
    fake_db("like_repository", rowcount=0)

    # Act / Assert
    assert _call("like_repository", "add_like", 1, 2) is False


@pytest.mark.parametrize("user_id, expect_filter", [(None, False), (5, True)])
def test_get_posts_paginated_optional_author_filter(fake_db, user_id, expect_filter):
    # Arrange
    _, cursor = fake_db("post_repository", fetchall=ROWS)

    # Act
    result = _call("post_repository", "get_posts_paginated", 0, 10, user_id)

    # Assert
    sql, params = cursor.execute.call_args[0]
    assert result == ROWS
    assert ("WHERE posts.author_id" in sql) == expect_filter
    assert params == ((5, 10, 0) if expect_filter else (10, 0))


def test_create_session_returns_uuid(fake_db):
    # Arrange
    _, cursor = fake_db("session_repository")

    # Act
    session_id = _call("session_repository", "create_session", 1, WHEN)

    # Assert
    assert len(session_id) == 36
    assert cursor.execute.call_args[0][1] == (session_id, 1, WHEN)


def test_update_user_profile_only_given_fields(fake_db):
    # Arrange
    _, cursor = fake_db("user_repository", rowcount=1)

    # Act
    result = _call("user_repository", "update_user_profile", 1, bio="Hello")

    # Assert
    sql, params = cursor.execute.call_args[0]
    assert result is True
    assert "bio = %s" in sql and "name = %s" not in sql
    assert params == ("Hello", 1)


def test_update_user_profile_all_fields(fake_db):
    # Arrange
    _, cursor = fake_db("user_repository", rowcount=1)

    # Act
    _call("user_repository", "update_user_profile", 1,
          name="Ann", bio="Hi", profile_picture="/p.jpg")

    # Assert
    assert cursor.execute.call_args[0][1] == ("Ann", "Hi", "/p.jpg", 1)


def test_update_user_profile_nothing_to_update(fake_db):
    # Arrange
    conn, _ = fake_db("user_repository")

    # Act
    result = _call("user_repository", "update_user_profile", 1)

    # Assert — returns early without touching the database
    assert result is False
    conn.cursor.return_value.execute.assert_not_called()


@pytest.mark.parametrize("banned, stored", [(True, 1), (False, 0)])
def test_set_user_banned_stores_int(fake_db, banned, stored):
    # Arrange
    _, cursor = fake_db("user_repository", rowcount=1)

    # Act
    _call("user_repository", "set_user_banned", 7, banned)

    # Assert
    assert cursor.execute.call_args[0][1] == (stored, 7)
