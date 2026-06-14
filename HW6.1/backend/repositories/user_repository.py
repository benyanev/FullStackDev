"""User repository — CRUD operations for the ``users`` table.

Every function opens its own connection, executes a single query, and
closes the connection.  No business logic lives here; validation and
orchestration belong in :mod:`services.user_service` or
:mod:`services.auth_service`.
"""

from core.database import get_connection


def get_user_by_id(user_id):
    """Look up a user by primary key.

    Args:
        user_id: The user's integer ID.

    Returns:
        A dict with id, name, email, bio, profile_picture, and created_at,
        or None if not found. The password_hash column is intentionally excluded.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, name, email, bio, profile_picture, created_at '
            'FROM users WHERE id = %s',
            (user_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email):
    """Look up a user by email address.

    Unlike get_user_by_id, this returns all columns (including
    password_hash) because it is used during login verification.

    Args:
        email: The email address to search for.

    Returns:
        A full user dict, or None if no match exists.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_users_paginated(start=0, limit=10):
    """Return a paginated list of users, ordered by newest first.

    Args:
        start: Pagination offset (default 0).
        limit: Maximum number of users to return (default 10).

    Returns:
        A list of user dicts (id, name, email, bio, profile_picture, created_at).
        The password_hash column is excluded for safety.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, name, email, bio, profile_picture, created_at FROM users '
            'ORDER BY created_at DESC LIMIT %s OFFSET %s',
            (limit, start)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def create_user(name, email, password_hash):
    """Insert a new user into the database.

    Args:
        name:          Display name.
        email:         Email address (must be unique).
        password_hash: Bcrypt-hashed password string.

    Returns:
        The auto-generated integer ID of the new user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)',
            (name, email, password_hash),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_user_profile(user_id, name=None, bio=None, profile_picture=None):
    """Update a user's profile fields.

    Only updates the fields that are provided (not None).

    Args:
        user_id:         The user's integer ID.
        name:            New display name (optional).
        bio:             New bio text (optional).
        profile_picture: New profile picture path (optional).

    Returns:
        True if the update affected a row, False otherwise.
    """
    fields = []
    values = []
    if name is not None:
        fields.append('name = %s')
        values.append(name)
    if bio is not None:
        fields.append('bio = %s')
        values.append(bio)
    if profile_picture is not None:
        fields.append('profile_picture = %s')
        values.append(profile_picture)

    if not fields:
        return False

    values.append(user_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f'UPDATE users SET {", ".join(fields)} WHERE id = %s',
            tuple(values),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()
