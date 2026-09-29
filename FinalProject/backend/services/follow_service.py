"""Follow service — follow/unfollow business logic and relationship queries.

Enforces rules like "cannot follow yourself" and "target must exist" at
the business layer, raising exceptions that controllers translate to
HTTP responses.
"""

from core.exceptions import NotFoundError, ValidationError
from repositories.follow_repository import (
    follow_user,
    get_followers,
    get_following,
    is_following,
    unfollow_user,
)
from repositories.user_repository import get_user_by_id


def follow(follower_id, target_id):
    """Follow a user.

    Args:
        follower_id: The authenticated user's ID.
        target_id:   The user to follow.

    Returns:
        A tuple ``(message, following_bool)``.

    Raises:
        ValidationError: If trying to follow yourself.
        NotFoundError:   If the target user doesn't exist.
    """
    if follower_id == target_id:
        raise ValidationError('You cannot follow yourself.')

    target = get_user_by_id(target_id)
    if target is None:
        raise NotFoundError('User not found.')

    created = follow_user(follower_id, target_id)
    message = 'Followed.' if created else 'Already following.'
    return message, True


def unfollow(follower_id, target_id):
    """Unfollow a user.

    Args:
        follower_id: The authenticated user's ID.
        target_id:   The user to unfollow.

    Returns:
        A tuple ``(message, following_bool)``.
    """
    removed = unfollow_user(follower_id, target_id)
    message = 'Unfollowed.' if removed else 'Was not following.'
    return message, False


def get_user_followers(user_id):
    """Return the list of users who follow this user.

    Args:
        user_id: The target user's ID.

    Returns:
        A list of user dicts.

    Raises:
        NotFoundError: If the target user doesn't exist.
    """
    target = get_user_by_id(user_id)
    if target is None:
        raise NotFoundError('User not found.')

    return get_followers(user_id)


def get_user_following(user_id):
    """Return the list of users this user follows.

    Args:
        user_id: The target user's ID.

    Returns:
        A list of user dicts.

    Raises:
        NotFoundError: If the target user doesn't exist.
    """
    target = get_user_by_id(user_id)
    if target is None:
        raise NotFoundError('User not found.')

    return get_following(user_id)


def check_is_following(follower_id, target_id):
    """Check if one user follows another.

    Args:
        follower_id: The authenticated user's ID.
        target_id:   The target user's ID.

    Returns:
        ``True`` if following, ``False`` otherwise.
    """
    return is_following(follower_id, target_id)
