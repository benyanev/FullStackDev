"""Comment service — business logic for creating and listing comments.

Validates inputs and checks that the target post exists before
creating a comment.
"""

from core.exceptions import NotFoundError, ValidationError
from repositories.comment_repository import (
    create_comment as repo_create_comment,
    get_comments_by_post,
)
from repositories.post_repository import get_post_by_id
from services.sentiment_service import ensure_not_toxic

MAX_COMMENT_LENGTH = 2000


def add_comment(post_id, author_id, body, parent_id=None):
    """Create a new comment on a post.

    Args:
        post_id:   The post to comment on.
        author_id: The authenticated user's ID.
        body:      Comment text (already stripped by the controller).
        parent_id: Optional parent comment ID for nesting.

    Returns:
        The auto-generated integer ID of the new comment.

    Raises:
        NotFoundError:   If the post doesn't exist.
        ValidationError: If the body is empty or too long.
        ModerationError: If the comment is flagged as toxic.
    """
    if not body:
        raise ValidationError('Comment body is required.')
    if len(body) > MAX_COMMENT_LENGTH:
        raise ValidationError(f'Comment is too long (max {MAX_COMMENT_LENGTH} characters).')

    post = get_post_by_id(post_id)
    if post is None:
        raise NotFoundError('Post not found.')

    # Block toxic comments before they are saved
    ensure_not_toxic(body)

    return repo_create_comment(post_id, author_id, body, parent_id)


def get_comments(post_id):
    """Return all comments for a post.

    Args:
        post_id: The post whose comments to retrieve.

    Returns:
        A dict ``{'comments': list, 'count': int}``.

    Raises:
        NotFoundError: If the post doesn't exist.
    """
    post = get_post_by_id(post_id)
    if post is None:
        raise NotFoundError('Post not found.')

    comments = get_comments_by_post(post_id)
    return {'comments': comments, 'count': len(comments)}
