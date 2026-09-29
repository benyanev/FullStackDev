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
from services.sentiment_service import ensure_not_toxic
from utils.file_helpers import is_upload_url

MAX_TITLE_LENGTH = 255      # posts.title is VARCHAR(255)
MAX_BODY_LENGTH = 20000     # rich-text HTML; posts.body is TEXT (64 KB)


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


def create_post(user_id, title, body, image_url, video_url=''):
    """Create a new post.

    Args:
        user_id:   The authenticated user's ID.
        title:     Post title (already stripped by the controller).
        body:      Post body (already stripped by the controller).
        image_url: Optional image URL (already stripped by the controller).
        video_url: Optional video URL (already stripped by the controller).

    Returns:
        The auto-generated integer ID of the new post.

    Raises:
        ValidationError: If title or body is missing or too long, both an
                         image and a video are attached, or a media URL is
                         not one of our uploads.
        ModerationError: If the title or body is flagged as toxic.
    """
    if not title or not body:
        raise ValidationError('Title and body are required.')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError(f'Title is too long (max {MAX_TITLE_LENGTH} characters).')
    if len(body) > MAX_BODY_LENGTH:
        raise ValidationError('Post is too long.')
    if image_url and video_url:
        raise ValidationError('Attach either an image or a video, not both.')
    # Media must be a file uploaded to this site (not an external URL)
    if (image_url and not is_upload_url(image_url, 'posts')) or             (video_url and not is_upload_url(video_url, 'videos')):
        raise ValidationError('Invalid media file.')

    # Block toxic posts before they are saved (title + body in one check)
    ensure_not_toxic(title, body)

    return repo_create_post(user_id, title, body, image_url, video_url)
