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
        A dict with id, name, email, bio, profile_picture, role, is_banned,
        is_agent, personality, and created_at, or None if not found. The password_hash column is
        intentionally excluded.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, name, email, bio, profile_picture, role, is_banned, '
            'is_agent, personality, created_at '
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
        A list of user dicts (id, name, email, bio, profile_picture, role,
        is_banned, is_agent, personality, created_at, followers_count,
        following_count). The password_hash column is excluded for safety.
        Follower counts come from subqueries — one query instead of 2 per user.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, name, email, bio, profile_picture, role, is_banned, '
            'is_agent, personality, created_at, '
            '(SELECT COUNT(*) FROM follows WHERE following_id = users.id) AS followers_count, '
            '(SELECT COUNT(*) FROM follows WHERE follower_id = users.id) AS following_count '
            'FROM users '
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


def update_password_hash(user_id, new_password_hash):
    """Update a user's password hash.

    Used by the password reset flow after validating the reset token.

    Args:
        user_id:           The user's integer ID.
        new_password_hash: The new bcrypt-hashed password string.

    Returns:
        True if the update affected a row, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE users SET password_hash = %s WHERE id = %s',
            (new_password_hash, user_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def set_user_banned(user_id, is_banned):
    """Ban or unban a user.

    Args:
        user_id:   The user's integer ID.
        is_banned: True to ban, False to unban.

    Returns:
        True if the row changed (MySQL reports 0 rows when the value is unchanged).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE users SET is_banned = %s WHERE id = %s',
            (1 if is_banned else 0, user_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def set_user_role(user_id, role):
    """Change a user's role ('user' or 'admin').

    Args:
        user_id: The user's integer ID.
        role:    The new role value.

    Returns:
        True if the row changed (MySQL reports 0 rows when the value is unchanged).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE users SET role = %s WHERE id = %s',
            (role, user_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def create_agent(name, email, password_hash, bio, personality):
    """Insert a new agent (bot) account.

    Args:
        name:          Display name.
        email:         Unique email address.
        password_hash: Bcrypt hash of a random password nobody knows.
        bio:           Public profile bio.
        personality:   Character description that drives the bot's content.

    Returns:
        The auto-generated integer ID of the new agent.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (name, email, password_hash, bio, is_agent, personality) '
            'VALUES (%s, %s, %s, %s, 1, %s)',
            (name, email, password_hash, bio, personality),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_active_agents():
    """Return all agent accounts that are not banned.

    Returns:
        A list of dicts with id, name, and personality.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, name, personality FROM users '
            'WHERE is_agent = 1 AND is_banned = 0'
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
