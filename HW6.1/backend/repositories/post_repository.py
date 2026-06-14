"""Post repository — CRUD operations for the ``posts`` table.

All queries join against the ``users`` table to include author info
(email, name) in the result set, matching the original API contract.
"""

from core.database import get_connection


def get_posts_paginated(start=0, limit=10, user_id=None):
    """Return a paginated list of posts, joined with author info.

    Each post dict includes the author's email and name via an
    INNER JOIN on the users table.

    Args:
        start:   Pagination offset (default 0).
        limit:   Maximum number of posts to return (default 10).
        user_id: If provided, return only posts by this author.

    Returns:
        A list of post dicts ordered by created_at descending.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if user_id:
            cursor.execute(
                'SELECT posts.id, posts.author_id AS userId, posts.title, '
                'posts.body, posts.image_url, posts.created_at, '
                'users.email, users.name AS authorName '
                'FROM posts '
                'JOIN users ON posts.author_id = users.id '
                'WHERE posts.author_id = %s '
                'ORDER BY posts.created_at DESC '
                'LIMIT %s OFFSET %s',
                (user_id, limit, start)
            )
        else:
            cursor.execute(
                'SELECT posts.id, posts.author_id AS userId, posts.title, '
                'posts.body, posts.image_url, posts.created_at, '
                'users.email, users.name AS authorName '
                'FROM posts '
                'JOIN users ON posts.author_id = users.id '
                'ORDER BY posts.created_at DESC '
                'LIMIT %s OFFSET %s',
                (limit, start)
            )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def create_post(author_id, title, body, image_url=''):
    """Insert a new post into the database.

    Args:
        author_id: The ID of the user creating the post.
        title:     Post title.
        body:      Post body text.
        image_url: Optional URL/path to an attached image.

    Returns:
        The auto-generated integer ID of the new post.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO posts (author_id, title, body, image_url) VALUES (%s, %s, %s, %s)',
            (author_id, title, body, image_url),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_following_posts_paginated(user_id, start=0, limit=10):
    """Return a paginated list of posts from users that the given user follows.

    Uses a JOIN across posts, users, and follows to filter posts to only
    those authored by users the current user follows.

    Args:
        user_id: The ID of the user whose following-feed to retrieve.
        start:   Pagination offset (default 0).
        limit:   Maximum number of posts to return (default 10).

    Returns:
        A list of post dicts ordered by created_at descending.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT posts.id, posts.author_id AS userId, posts.title, '
            'posts.body, posts.image_url, posts.created_at, '
            'users.email, users.name AS authorName '
            'FROM posts '
            'JOIN users ON posts.author_id = users.id '
            'JOIN follows ON posts.author_id = follows.following_id '
            'WHERE follows.follower_id = %s '
            'ORDER BY posts.created_at DESC '
            'LIMIT %s OFFSET %s',
            (user_id, limit, start)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
