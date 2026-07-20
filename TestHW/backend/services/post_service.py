"""Post service — post creation and feed retrieval.

Delegates data access to :mod:`repositories.post_repository` and
performs input validation before writes.
"""

from core.exceptions import ValidationError
from repositories.post_repository import (
    create_post as repo_create_post,
    get_following_posts_paginated,
    get_posts_paginated,
)


def get_posts(start, limit, user_id=None):
    """Return a paginated list of posts.

    Args:
        start:   Pagination offset.
        limit:   Maximum number of posts.
        user_id: Optional author filter.

    Returns:
        A list of post dicts.
    """
    return get_posts_paginated(start, limit, user_id)


def get_following_posts(user_id, start, limit):
    """Return a paginated list of posts from followed users.

    Args:
        user_id: The authenticated user's ID.
        start:   Pagination offset.
        limit:   Maximum number of posts.

    Returns:
        A list of post dicts.
    """
    return get_following_posts_paginated(user_id, start, limit)


def create_post(user_id, title, body, image_url):
    """Create a new post.

    Args:
        user_id:   The authenticated user's ID.
        title:     Post title (already stripped by the controller).
        body:      Post body (already stripped by the controller).
        image_url: Optional image URL (already stripped by the controller).

    Returns:
        The auto-generated integer ID of the new post.

    Raises:
        ValidationError: If title or body is missing.
    """
    if not title or not body:
        raise ValidationError('Title and body are required.')

    return repo_create_post(user_id, title, body, image_url)
