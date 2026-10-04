"""Reset repository — CRUD operations for the ``password_resets`` table.

Handles creating, finding, and marking reset tokens as used.
"""

from core.database import get_connection


def create_reset_token(user_id, token, expires_at):
    """Insert a new password reset token.

    Args:
        user_id:    The user requesting the reset.
        token:      A unique 64-character hex string.
        expires_at: Datetime when the token expires.

    Returns:
        The auto-generated ID of the new reset record.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO password_resets (user_id, token, expires_at) '
            'VALUES (%s, %s, %s)',
            (user_id, token, expires_at),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_reset_by_token(token):
    """Look up a reset record by its token string.

    Args:
        token: The 64-character hex token.

    Returns:
        A dict with id, user_id, token, expires_at, used, created_at,
        or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT * FROM password_resets WHERE token = %s',
            (token,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def mark_token_used(token):
    """Mark a reset token as used so it cannot be reused.

    Args:
        token: The 64-character hex token.

    Returns:
        True if a row was updated, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE password_resets SET used = 1 WHERE token = %s',
            (token,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def invalidate_user_tokens(user_id):
    """Mark all existing tokens for a user as used.

    Called before creating a new token to prevent token flooding.

    Args:
        user_id: The user whose tokens to invalidate.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE password_resets SET used = 1 WHERE user_id = %s AND used = 0',
            (user_id,),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
