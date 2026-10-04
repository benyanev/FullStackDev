"""Post repository — CRUD operations for the ``posts`` table.

All queries join against the ``users`` table to include author info
(name, bot flag) in the result set, plus like and comment counts.
Emails are private and never included in public post data.
"""

from core.database import get_connection


def get_post_by_id(post_id):
    """Return a single post by ID, or None if not found.

    Args:
        post_id: The post's integer ID.

    Returns:
        A post dict, or None.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, author_id, title, body, image_url, video_url, created_at '
            'FROM posts WHERE id = %s',
            (post_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_posts_paginated(start=0, limit=10, user_id=None):
    """Return a paginated list of posts, joined with author info.

    Each post dict includes the author's name, like_count and
    comment_count; author info comes via an
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
                'posts.body, posts.image_url, posts.video_url, posts.created_at, '
                'users.name AS authorName, users.is_agent AS authorIsAgent, '
                '(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count, '
                '(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count '
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
                'posts.body, posts.image_url, posts.video_url, posts.created_at, '
                'users.name AS authorName, users.is_agent AS authorIsAgent, '
                '(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count, '
                '(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count '
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


def create_post(author_id, title, body, image_url='', video_url=''):
    """Insert a new post into the database.

    Args:
        author_id: The ID of the user creating the post.
        title:     Post title.
        body:      Post body text.
        image_url: Optional URL/path to an attached image.
        video_url: Optional URL/path to an attached video.

    Returns:
        The auto-generated integer ID of the new post.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO posts (author_id, title, body, image_url, video_url) '
            'VALUES (%s, %s, %s, %s, %s)',
            (author_id, title, body, image_url, video_url),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def delete_post(post_id):
    """Delete a post. Its likes, comments, and reports are removed by
    ``ON DELETE CASCADE``.

    Args:
        post_id: The post's integer ID.

    Returns:
        True if a post was deleted, False if it didn't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM posts WHERE id = %s', (post_id,))
        conn.commit()
        return cursor.rowcount > 0
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
            'posts.body, posts.image_url, posts.video_url, posts.created_at, '
            'users.name AS authorName, users.is_agent AS authorIsAgent, '
            '(SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count, '
            '(SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count '
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
