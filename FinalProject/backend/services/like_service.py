"""Like service — business logic for liking and unliking posts.

Validates that the target post exists before toggling likes.
"""

from core.exceptions import NotFoundError
from repositories.like_repository import (
    add_like,
    get_like_count,
    has_user_liked,
    remove_like,
)
from repositories.post_repository import get_post_by_id


def toggle_like(user_id, post_id):
    """Like a post if not liked, unlike if already liked.

    Args:
        user_id: The authenticated user's ID.
        post_id: The post to toggle like on.

    Returns:
        A dict ``{'liked': bool, 'likeCount': int}``.

    Raises:
        NotFoundError: If the post doesn't exist.
    """
    post = get_post_by_id(post_id)
    if post is None:
        raise NotFoundError('Post not found.')

    if has_user_liked(user_id, post_id):
        remove_like(user_id, post_id)
        liked = False
    else:
        add_like(user_id, post_id)
        liked = True

    count = get_like_count(post_id)
    return {'liked': liked, 'likeCount': count}


def get_post_likes(user_id, post_id):
    """Get the like count and whether the current user has liked a post.

    Args:
        user_id: The authenticated user's ID (or None if not logged in).
        post_id: The post to check.

    Returns:
        A dict ``{'liked': bool, 'likeCount': int}``.

    Raises:
        NotFoundError: If the post doesn't exist.
    """
    post = get_post_by_id(post_id)
    if post is None:
        raise NotFoundError('Post not found.')

    count = get_like_count(post_id)
    liked = has_user_liked(user_id, post_id) if user_id else False
    return {'liked': liked, 'likeCount': count}
