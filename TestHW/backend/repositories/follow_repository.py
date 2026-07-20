"""Follow repository — CRUD operations for the ``follows`` table.

Handles follower/following relationships including counts and list
queries with user JOIN data.
"""

from core.database import get_connection


def follow_user(follower_id, following_id):
    """Create a follow relationship.

    Uses INSERT IGNORE to silently skip if the relationship already exists
    (prevented by the composite primary key).

    Args:
        follower_id:  The user who is following.
        following_id: The user being followed.

    Returns:
        True if a new follow was created, False if it already existed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT IGNORE INTO follows (follower_id, following_id) VALUES (%s, %s)',
            (follower_id, following_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def unfollow_user(follower_id, following_id):
    """Remove a follow relationship.

    Args:
        follower_id:  The user who is unfollowing.
        following_id: The user being unfollowed.

    Returns:
        True if a follow was removed, False if it didn't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'DELETE FROM follows WHERE follower_id = %s AND following_id = %s',
            (follower_id, following_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def is_following(follower_id, following_id):
    """Check if one user follows another.

    Args:
        follower_id:  The potential follower.
        following_id: The potentially followed user.

    Returns:
        True if follower_id follows following_id, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT 1 FROM follows WHERE follower_id = %s AND following_id = %s',
            (follower_id, following_id),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


def get_followers_count(user_id):
    """Return the number of users who follow this user.

    Args:
        user_id: The user whose follower count to retrieve.

    Returns:
        Integer count of followers.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT COUNT(*) FROM follows WHERE following_id = %s',
            (user_id,),
        )
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def get_following_count(user_id):
    """Return the number of users this user follows.

    Args:
        user_id: The user whose following count to retrieve.

    Returns:
        Integer count of users being followed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT COUNT(*) FROM follows WHERE follower_id = %s',
            (user_id,),
        )
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def get_followers(user_id):
    """Return the list of users who follow this user.

    Args:
        user_id: The user whose followers to retrieve.

    Returns:
        A list of user dicts (id, name, email, created_at).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT users.id, users.name, users.email, users.created_at '
            'FROM follows '
            'JOIN users ON follows.follower_id = users.id '
            'WHERE follows.following_id = %s '
            'ORDER BY follows.created_at DESC',
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_following(user_id):
    """Return the list of users this user follows.

    Args:
        user_id: The user whose following list to retrieve.

    Returns:
        A list of user dicts (id, name, email, created_at).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT users.id, users.name, users.email, users.created_at '
            'FROM follows '
            'JOIN users ON follows.following_id = users.id '
            'WHERE follows.follower_id = %s '
            'ORDER BY follows.created_at DESC',
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
