"""User service — user retrieval and profile management.

Orchestrates repository calls and enriches results with follower/following
counts.  Profile authorization checks live here rather than in the
controller so that the rule "only the owner can edit" is enforced at the
business layer.
"""

from core.exceptions import ForbiddenError, NotFoundError, ValidationError
from repositories.follow_repository import get_followers_count, get_following_count
from repositories.user_repository import get_user_by_id, get_users_paginated, update_user_profile


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
        A list of user dicts.
    """
    users = get_users_paginated(start, limit)
    for user in users:
        _enrich_with_counts(user)
    return users


def get_single_user(user_id):
    """Return a single user by ID with follower/following counts.

    Args:
        user_id: The user's integer ID.

    Returns:
        A user dict.

    Raises:
        NotFoundError: If the user does not exist.
    """
    user = get_user_by_id(user_id)
    if user is None:
        raise NotFoundError('User not found.')
    _enrich_with_counts(user)
    return user


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
        ValidationError: If the name is provided but empty.
        ValidationError: If no changes were made.
    """
    if requesting_user_id != user_id:
        raise ForbiddenError('You can only edit your own profile.')

    if name is not None and not name.strip():
        raise ValidationError('Name cannot be empty.')

    updated = update_user_profile(
        user_id,
        name=name.strip() if name else None,
        bio=bio,
        profile_picture=profile_picture,
    )

    if not updated:
        raise ValidationError('No changes made.')

    user = get_user_by_id(user_id)
    _enrich_with_counts(user)
    return user
