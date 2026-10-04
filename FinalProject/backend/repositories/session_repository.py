"""Session repository — CRUD operations for the ``sessions`` table.

Sessions use UUID primary keys and support expiry-based cleanup.
"""

import uuid

from core.database import get_connection


def create_session(user_id, expires_at):
    """Create a new session for a user and return the session UUID.

    Args:
        user_id:    The user's integer ID.
        expires_at: A datetime marking when the session becomes invalid.

    Returns:
        A 36-character UUID string representing the session ID.
    """
    session_id = str(uuid.uuid4())
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO sessions (id, user_id, expires_at) VALUES (%s, %s, %s)',
            (session_id, user_id, expires_at),
        )
        conn.commit()
        return session_id
    finally:
        cursor.close()
        conn.close()


def get_session(session_id):
    """Look up a session by its UUID, together with the user's ban status.

    Args:
        session_id: The 36-character UUID string.

    Returns:
        A dict with id, user_id, expires_at, and is_banned, or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT sessions.id, sessions.user_id, sessions.expires_at, users.is_banned '
            'FROM sessions JOIN users ON users.id = sessions.user_id '
            'WHERE sessions.id = %s',
            (session_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def delete_session(session_id):
    """Delete a single session (used for logout).

    Args:
        session_id: The 36-character UUID string to remove.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM sessions WHERE id = %s', (session_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_user_sessions(user_id):
    """Delete all sessions for a user (called before creating a new login session).

    Args:
        user_id: The user's integer ID.

    Returns:
        The number of sessions that were deleted.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM sessions WHERE user_id = %s', (user_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def delete_expired_sessions():
    """Remove all sessions whose expires_at is in the past.

    Call this periodically (e.g. on startup or via a scheduled task)
    to prevent the sessions table from growing unbounded.

    Returns:
        The number of expired sessions that were deleted.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM sessions WHERE expires_at < NOW()')
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()
