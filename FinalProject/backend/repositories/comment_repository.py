"""Comment repository — CRUD operations for the ``comments`` table.

Handles creating comments and fetching comments for a post,
with author info joined from the users table.
"""

from core.database import get_connection


def create_comment(post_id, author_id, body, parent_id=None):
    """Insert a new comment.

    Args:
        post_id:   The post this comment belongs to.
        author_id: The user writing the comment.
        body:      Comment text.
        parent_id: Optional parent comment ID for nesting.

    Returns:
        The auto-generated integer ID of the new comment.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO comments (post_id, author_id, body, parent_id) '
            'VALUES (%s, %s, %s, %s)',
            (post_id, author_id, body, parent_id),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_comments_by_post(post_id):
    """Return all comments for a post, joined with author info.

    Comments are returned in chronological order (oldest first)
    so the frontend can display them naturally.

    Args:
        post_id: The post whose comments to retrieve.

    Returns:
        A list of comment dicts with the author's name (emails stay private).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT comments.id, comments.post_id, comments.author_id, '
            'comments.parent_id, comments.body, comments.created_at, '
            'users.name AS authorName, users.is_agent AS authorIsAgent '
            'FROM comments '
            'JOIN users ON comments.author_id = users.id '
            'WHERE comments.post_id = %s '
            'ORDER BY comments.created_at ASC',
            (post_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
