"""Report service — lets users flag a post for moderator review.

Validates the reason, checks the post exists, blocks self-reports and
duplicate reports.  Handling the reports is done in
:mod:`services.admin_service`.
"""

from core.exceptions import ConflictError, NotFoundError, ValidationError
from repositories.post_repository import get_post_by_id
from repositories.report_repository import create_report as repo_create_report

MAX_REASON_LENGTH = 500


def create_report(reporter_id, post_id, reason):
    """Report a post.

    Args:
        reporter_id: The authenticated user's ID.
        post_id:     The post being reported.
        reason:      Why the post is being reported (already stripped).

    Raises:
        ValidationError: If the reason is missing/too long, or the user
                         reports their own post.
        NotFoundError:   If the post doesn't exist.
        ConflictError:   If this user already reported this post.
    """
    if not reason:
        raise ValidationError('Please give a reason for the report.')
    if len(reason) > MAX_REASON_LENGTH:
        raise ValidationError(f'Reason must be at most {MAX_REASON_LENGTH} characters.')

    post = get_post_by_id(post_id)
    if post is None:
        raise NotFoundError('Post not found.')
    if post['author_id'] == reporter_id:
        raise ValidationError('You cannot report your own post.')

    if not repo_create_report(reporter_id, post_id, reason):
        raise ConflictError('You already reported this post.')
