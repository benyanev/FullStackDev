"""Report repository — CRUD operations for the ``reports`` table.

A report is a user flagging a post for moderator review.  Pending reports
are listed on the Admin Dashboard together with post and user info.
"""

from core.database import get_connection


def create_report(reporter_id, post_id, reason):
    """Insert a report. Uses INSERT IGNORE to skip duplicates.

    Args:
        reporter_id: The user who is reporting.
        post_id:     The reported post.
        reason:      Free-text reason given by the reporter.

    Returns:
        True if a new report was created, False if this user already
        reported this post.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT IGNORE INTO reports (reporter_id, post_id, reason) '
            'VALUES (%s, %s, %s)',
            (reporter_id, post_id, reason),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def get_pending_reports():
    """Return all pending reports, newest first, with post and user info.

    Returns:
        A list of report dicts including the post title/body, the post
        author's id/name/ban status, and the reporter's name.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT reports.id, reports.post_id, reports.reason, reports.status, '
            'reports.created_at, '
            'posts.title AS post_title, posts.body AS post_body, '
            'author.id AS author_id, author.name AS author_name, '
            'author.is_banned AS author_is_banned, '
            'reporter.id AS reporter_id, reporter.name AS reporter_name '
            'FROM reports '
            'JOIN posts ON reports.post_id = posts.id '
            'JOIN users AS author ON posts.author_id = author.id '
            'JOIN users AS reporter ON reports.reporter_id = reporter.id '
            "WHERE reports.status = 'pending' "
            'ORDER BY reports.created_at DESC'
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def update_report_status(report_id, status):
    """Set a report's status ('resolved' or 'dismissed').

    Args:
        report_id: The report's integer ID.
        status:    The new status value.

    Returns:
        True if a report was updated, False if it doesn't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE reports SET status = %s WHERE id = %s',
            (status, report_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()
