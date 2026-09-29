"""Admin service — moderator actions for the Admin Dashboard.

Handles reviewing reports, deleting posts, banning users, and
promoting/demoting moderators.  Access control (admin only) is enforced
by the ``admin_required`` decorator on the routes.
"""

from core.exceptions import NotFoundError, ValidationError
from repositories.post_repository import delete_post as repo_delete_post
from repositories.report_repository import get_pending_reports, update_report_status
from repositories.session_repository import delete_user_sessions
from repositories.user_repository import (
    get_user_by_id,
    get_users_paginated,
    set_user_banned,
    set_user_role,
)

REPORT_STATUSES = ('resolved', 'dismissed')
ROLES = ('user', 'admin')


def get_reports():
    """Return all pending reports for the dashboard."""
    return get_pending_reports()


def update_report(report_id, status):
    """Mark a report as resolved or dismissed.

    Raises:
        ValidationError: If the status is not 'resolved' or 'dismissed'.
        NotFoundError:   If the report doesn't exist.
    """
    if status not in REPORT_STATUSES:
        raise ValidationError("Status must be 'resolved' or 'dismissed'.")
    if not update_report_status(report_id, status):
        raise NotFoundError('Report not found.')


def delete_post(post_id):
    """Delete an offending post (its reports are deleted with it).

    Raises:
        NotFoundError: If the post doesn't exist.
    """
    if not repo_delete_post(post_id):
        raise NotFoundError('Post not found.')


def get_users(start, limit):
    """Return a page of users including their role and ban status."""
    return get_users_paginated(start, limit)


def _get_other_user(admin_id, user_id, action):
    """Return the target user, refusing actions on the admin themselves."""
    if user_id == admin_id:
        raise ValidationError(f'You cannot {action} yourself.')
    user = get_user_by_id(user_id)
    if user is None:
        raise NotFoundError('User not found.')
    return user


def set_ban(admin_id, user_id, banned):
    """Ban or unban a user. Banning also logs them out everywhere.

    Raises:
        ValidationError: If the admin targets themselves.
        NotFoundError:   If the user doesn't exist.
    """
    _get_other_user(admin_id, user_id, 'ban' if banned else 'unban')
    set_user_banned(user_id, banned)
    if banned:
        delete_user_sessions(user_id)


def set_role(admin_id, user_id, role):
    """Promote a user to admin (moderator) or demote them back to user.

    Raises:
        ValidationError: If the role is invalid or the admin targets themselves.
        NotFoundError:   If the user doesn't exist.
    """
    if role not in ROLES:
        raise ValidationError("Role must be 'user' or 'admin'.")
    _get_other_user(admin_id, user_id, 'change the role of')
    set_user_role(user_id, role)
