"""Like repository — CRUD operations for the ``likes`` table.

Handles toggling likes (insert/delete) and querying like counts
and per-user like status for posts.
"""

from core.database import get_connection


def add_like(user_id, post_id):
    """Insert a like. Uses INSERT IGNORE to skip duplicates.

    Args:
        user_id: The user who is liking.
        post_id: The post being liked.

    Returns:
        True if a new like was created, False if it already existed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT IGNORE INTO likes (user_id, post_id) VALUES (%s, %s)',
            (user_id, post_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def remove_like(user_id, post_id):
    """Remove a like.

    Args:
        user_id: The user who is unliking.
        post_id: The post being unliked.

    Returns:
        True if a like was removed, False if it didn't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'DELETE FROM likes WHERE user_id = %s AND post_id = %s',
            (user_id, post_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def get_like_count(post_id):
    """Return the number of likes on a post.

    Args:
        post_id: The post to count likes for.

    Returns:
        Integer like count.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT COUNT(*) FROM likes WHERE post_id = %s',
            (post_id,),
        )
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def has_user_liked(user_id, post_id):
    """Check if a user has liked a post.

    Args:
        user_id: The user to check.
        post_id: The post to check.

    Returns:
        True if the user has liked the post, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT 1 FROM likes WHERE user_id = %s AND post_id = %s',
            (user_id, post_id),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()
