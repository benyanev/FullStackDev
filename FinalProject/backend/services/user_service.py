"""User service — user retrieval and profile management.

Orchestrates repository calls and enriches results with follower/following
counts.  Profile authorization checks live here rather than in the
controller so that the rule "only the owner can edit" is enforced at the
business layer.
"""

from core.exceptions import ForbiddenError, NotFoundError, ValidationError
from repositories.follow_repository import get_followers_count, get_following_count
from repositories.user_repository import get_user_by_id, get_users_paginated, update_user_profile
from utils.file_helpers import is_upload_url

MAX_NAME_LENGTH = 100   # users.name is VARCHAR(100)
MAX_BIO_LENGTH = 500


# Private account data — only shown to the user themselves (/api/me) and admins
PRIVATE_FIELDS = ('email', 'role', 'is_banned')


def _public(user):
    """Remove private fields before a user is shown to other people."""
    for field in PRIVATE_FIELDS:
        user.pop(field, None)
    return user


def _enrich_with_counts(user):
    """Attach ``followers_count`` and ``following_count`` to a user dict."""
    user['followers_count'] = get_followers_count(user['id'])
    user['following_count'] = get_following_count(user['id'])
    return user


def get_users(start, limit):
    """Return a paginated list of users with follower/following counts.

    Args:
        start: Pagination offset.
        limit: Maximum number of users.

    Returns:
        A list of public user dicts (follower counts included by the query).
    """
    return [_public(user) for user in get_users_paginated(start, limit)]


def get_single_user(user_id):
    """Return a single user by ID with follower/following counts.

    Args:
        user_id: The user's integer ID.

    Returns:
        A public user dict (no email / role / ban status).

    Raises:
        NotFoundError: If the user does not exist.
    """
    user = get_user_by_id(user_id)
    if user is None:
        raise NotFoundError('User not found.')
    _enrich_with_counts(user)
    return _public(user)


def update_profile(user_id, requesting_user_id, name=None, bio=None, profile_picture=None):
    """Update a user's profile.

    Args:
        user_id:            The profile owner's ID (from the URL).
        requesting_user_id: The authenticated user's ID (from the session).
        name:               New display name (optional).
        bio:                New bio text (optional).
        profile_picture:    New profile picture path (optional).

    Returns:
        The updated user dict with follower/following counts.

    Raises:
        ForbiddenError:  If the requesting user is not the profile owner.
        ValidationError: If the name is empty/too long, the bio is too long,
                         the picture is not one of our uploads, or no
                         field was given at all.
    """
    if requesting_user_id != user_id:
        raise ForbiddenError('You can only edit your own profile.')

    if name is None and bio is None and profile_picture is None:
        raise ValidationError('Nothing to update.')
    if name is not None and not name.strip():
        raise ValidationError('Name cannot be empty.')
    if name is not None and len(name.strip()) > MAX_NAME_LENGTH:
        raise ValidationError(f'Name is too long (max {MAX_NAME_LENGTH} characters).')
    if bio is not None and len(bio) > MAX_BIO_LENGTH:
        raise ValidationError(f'Bio is too long (max {MAX_BIO_LENGTH} characters).')
    if profile_picture and not is_upload_url(profile_picture, 'profiles'):
        raise ValidationError('Invalid profile picture.')

    # Saving without changing anything is fine (MySQL just reports 0 changed rows)
    update_user_profile(
        user_id,
        name=name.strip() if name else None,
        bio=bio,
        profile_picture=profile_picture,
    )

    user = get_user_by_id(user_id)
    _enrich_with_counts(user)
    return user
